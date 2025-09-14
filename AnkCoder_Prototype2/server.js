const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const bodyParser = require("body-parser");

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Connect to MongoDB
mongoose.connect("mongodb://127.0.0.1:27017/ank")
.then(()=> console.log("DB Connected"))
.catch(err => console.log("DB Error:", err));

// Schema
const UserSchema = new mongoose.Schema({
  firstName: String,
  middleName: String,
  lastName: String,
  dob: String,
  gender: String,
  mob: String,
  nameNumber: Number,
  dobNumber: Number,
  moolank: Number,
  bhagyank: Number,
  destiny: Number
});

const User = mongoose.model("User", UserSchema);

// API route
app.post("/saveUser", async (req, res) => {
  try {
    const user = new User(req.body);
    await user.save();
    res.json({ message: "✅ User saved successfully!" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Error saving user" });
  }
});

app.listen(3000, () => console.log("Server running on http://localhost:3000"));
