const chaldeanMap = {
  A:1, I:1, J:1, Q:1, Y:1,
  B:2, K:2, R:2,
  C:3, G:3, L:3, S:3,
  D:4, M:4, T:4,
  E:5, H:5, N:5, X:5,
  U:6, V:6, W:6,
  O:7, Z:7,
  F:8, P:8
};

function reduceToSingleDigit(num) {
  while (num > 9) {
    num = num.toString().split('').reduce((a,b)=>a+parseInt(b),0);
  }
  return num;
}

function calculateNumerology() {
  let first = document.getElementById("firstName").value.toUpperCase();
  let middle = document.getElementById("middleName").value.toUpperCase();
  let last = document.getElementById("lastName").value.toUpperCase();
  let dob = document.getElementById("dob").value;

  let fullName = (first + middle + last).replace(/[^A-Z]/g, "");
  let nameSum = 0;
  for (let ch of fullName) {
    if (chaldeanMap[ch]) nameSum += chaldeanMap[ch];
  }
  let nameNumber = reduceToSingleDigit(nameSum);

  let dobDigits = dob.replace(/-/g, "").split("").map(Number);
  let dobSum = dobDigits.reduce((a,b)=>a+b,0);
  let dobNumber = reduceToSingleDigit(dobSum);

  document.getElementById("nameResult").innerText = "Name Number: " + nameNumber;
  document.getElementById("dobResult").innerText = "DOB Number: " + dobNumber;
  document.getElementById("result").style.display = "block";
}
