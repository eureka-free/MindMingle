from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML formunu içeren basit bir sayfa
HTML_FORM = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ruh Halini Belirle</title>
</head>
<body>
    <h1>Ruh Halinizi Belirtin</h1>
    <form action="/submit-mood" method="post">
        <label for="mood">Bugün nasıl hissediyorsunuz?</label>
        <select name="mood" id="mood">
            <option value="happy">Mutlu</option>
            <option value="sad">Üzgün</option>
            <option value="angry">Sinirli</option>
            <option value="relaxed">Rahat</option>
        </select>
        <button type="submit">Gönder</button>
    </form>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_FORM)

@app.route('/submit-mood', methods=['POST'])
def submit_mood():
    # Formdan gelen ruh hali bilgisini al
    mood = request.form['mood']
    return f"<h1>Ruh Haliniz: {mood}</h1>"

if __name__ == "__main__":
    app.run(debug=True)
