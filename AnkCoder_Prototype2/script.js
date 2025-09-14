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
  while (num > 9 && num !== 11 && num !== 22) {
    num = num.toString().split('').reduce((a,b)=>a+parseInt(b),0);
  }
  return num;
}

function generateLoShuGrid(digits) {
  const loshuPattern = {1:7, 2:2, 3:3, 4:1, 5:4, 6:8, 7:5, 8:6, 9:0};
  let grid = ["","","","","","","","",""];
  digits.forEach(d => {
    if(d!==0 && loshuPattern[d]!==undefined){
      let pos = loshuPattern[d];
      grid[pos] += d;
    }
  });
  const gridContainer = document.getElementById("loshuGrid");
  gridContainer.innerHTML = "";
  grid.forEach(val=>{
    let cell = document.createElement("div");
    cell.innerText = val || "-";
    gridContainer.appendChild(cell);
  });
}

async function calculateNumerology() {
  let first = document.getElementById("firstName").value;
  let middle = document.getElementById("middleName").value;
  let last = document.getElementById("lastName").value;
  let dob = document.getElementById("dob").value;
  let gender = document.getElementById("gender").value;
  let mob = document.getElementById("mob").value;

  if(!first || !last || !dob || !mob){
    alert("Please fill all required fields!");
    return;
  }

  // Uppercase for calculation
  let firstUpper = first.toUpperCase();
  let middleUpper = middle.toUpperCase();
  let lastUpper = last.toUpperCase();

  let fullName = (firstUpper + middleUpper + lastUpper).replace(/[^A-Z]/g,"");
  let nameSum = 0;
  for(let ch of fullName) if(chaldeanMap[ch]) nameSum += chaldeanMap[ch];
  let nameNumber = reduceToSingleDigit(nameSum);

  let dobDigits = dob.replace(/-/g,"").split("").map(Number);
  let dobSum = dobDigits.reduce((a,b)=>a+b,0);
  let dobNumber = reduceToSingleDigit(dobSum);

  let day = parseInt(dob.split("-")[2]);
  let moolank = reduceToSingleDigit(day);

  let [year, month, date] = dob.split("-").map(Number);
  let bhagyank = reduceToSingleDigit(year+month+date);

  let destiny = reduceToSingleDigit(dobSum);

  // Update results
  document.getElementById("nameResult").innerText = "Name Number: "+nameNumber;
  document.getElementById("dobResult").innerText = "Luck Number: "+dobNumber;
  document.getElementById("moolankResult").innerText = "Moolank (Birth Number): "+moolank;
  document.getElementById("bhagyankResult").innerText = "Bhagyank (Destiny Number): "+bhagyank;
  document.getElementById("destinyResult").innerText = "Destiny Number: "+destiny;

  generateLoShuGrid([...dobDigits, moolank, bhagyank, destiny]);
  document.getElementById("result").style.display = "block";

  // Save to backend
  const userData = { firstName:first, middleName:middle, lastName:last, dob, gender, mob, nameNumber, dobNumber, moolank, bhagyank, destiny };

  try{
    const res = await fetch("http://localhost:3000/saveUser", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(userData)
    });
    const result = await res.json();
    document.getElementById("statusMessage").style.color = "green";
    document.getElementById("statusMessage").innerText = result.message;
    console.log("Saved:", result);
  } catch(err){
    console.error(err);
    document.getElementById("statusMessage").style.color = "red";
    document.getElementById("statusMessage").innerText = "Failed to save user!";
  }
}
