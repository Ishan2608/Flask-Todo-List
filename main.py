from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime, date

app = Flask(__name__)

items = []
history = []
editing_id = None
next_id = 1

week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
          'September', 'October', 'November', 'December']

now = datetime.now()
year, month, day = now.year, now.month, now.day
weekday = now.weekday()
week_day = week_days[weekday]
month_name = months[month - 1]
curr_day = f'{day} {month_name} {year}, {week_day}'

@app.route('/', methods=['GET', 'POST'])
def home():
    global next_id
    if request.method == 'POST':
        form_data = request.form
        new_item_content = form_data.get('newItem', '').strip()
        new_item_duedate = form_data.get('duedate', '')
        new_item_category = form_data.get('category', '')

        if not new_item_content:
            return redirect(url_for('home'))

        try:
            due_year, due_month, due_day = map(int, new_item_duedate.split("-"))
        except (ValueError, AttributeError):
            return redirect(url_for('home'))

        new_item = {
            'id': next_id,
            'content': new_item_content,
            'category': new_item_category,
            'due_date': {
                'year': due_year,
                'month': due_month,
                'day': due_day
            }
        }
        next_id += 1
        items.append(new_item)

        for item in items:
            due = item['due_date']
            due_date_obj = date(due['year'], due['month'], due['day'])
            item['overdue'] = due_date_obj < date.today()

        items.sort(key=lambda item: date(item['due_date']['year'], item['due_date']['month'], item['due_date']['day']))

        return redirect(url_for('home'))

    return render_template('index.html', list_items=items, today=curr_day, leng=len(items), editing_id=editing_id, history=history)

@app.route('/delete-item', methods=['POST'])
def delete_item():
    if request.method == 'POST':
        form = request.form
        try:
            id = int(form['checkbox'])
        except (KeyError, ValueError):
            return redirect(url_for('home'))

        target = next((item for item in items if item['id'] == id), None)
        if target:
            history.append({
                **target,
                'status': 'Deleted',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            items.remove(target)
        return redirect(url_for('home'))

@app.route('/complete-item', methods=['POST'])
def complete_item():
    if request.method == 'POST':
        form = request.form
        try:
            id = int(form['complete_id'])
        except (KeyError, ValueError):
            return redirect(url_for('home'))

        target = next((item for item in items if item['id'] == id), None)
        if target:
            history.append({
                **target,
                'status': 'Completed',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            items.remove(target)
        return redirect(url_for('home'))

@app.route('/set-edit/<int:item_id>')
def set_edit(item_id):
    global editing_id
    editing_id = item_id
    return redirect(url_for('home'))

@app.route('/edit-item', methods=['POST'])
def edit_item():
    global editing_id
    form = request.form
    try:
        edit_id = int(form['edit_id'])
        new_content = form['new_content'].strip()
    except (KeyError, ValueError):
        return redirect(url_for('home'))

    for item in items:
        if item['id'] == edit_id:
            item['content'] = new_content
            break

    editing_id = None
    return redirect(url_for('home'))

# pragma: no cover
if __name__ == '__main__': 
    app.run(debug=True)