const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const app = express();

app.use(bodyParser.urlencoded({ extended: true })); // Для форми з текстовими полями
app.use(bodyParser.json()); // Для JSON-формату

// Підключення до MongoDB
mongoose.connect('mongodb+srv://taras:23atuges@clicktype.jpsd4.mongodb.net/?retryWrites=true&w=majority&appName=clicktype')
  .then(() => console.log('Connected to MongoDB Atlas!'))
  .catch(err => console.error('Error connecting to MongoDB Atlas:', err));

// Модель користувача (тільки пошта та пароль)
const UserSchema = new mongoose.Schema({
  email: { type: String, required: true },
  password: { type: String, required: true }
});

const User = mongoose.model('User', UserSchema);

// Статичні файли
app.use(express.static('public'));

// Обробка маршруту для login.html
app.get('/login', (req, res) => {
  res.sendFile(__dirname + '/public/login.html');
});

// Обробка форми для збереження користувача
app.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;  // Отримуємо дані з форми
    const user = new User({ email, password });
    await user.save();  // Зберігаємо дані в базі

    res.status(200).send('User registered successfully');
  } catch (err) {
    console.error('Error saving user:', err);
    res.status(500).send('Error saving user');
  }
});

// Запуск сервера
app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});