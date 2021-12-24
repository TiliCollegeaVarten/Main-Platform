const backDrop = document.getElementById("back-drop");
const input = document.getElementById("input");
const questionContainer = document.getElementById("question");
const nextBtn = document.getElementById("next-btn");
const paraEl = document.createElement("p");

let questionNumber = 0;

const questions = [
  {
    question: "Hello1",
    hint: "H",
  },
  {
    question: "Hello2",
    hint: "H",
  },
  {
    question: "Hello3",
    hint: "H",
  },
];

function showNextQuestions() {
  paraEl.innerText = questions[questionNumber].question;
  questionContainer.appendChild(paraEl);
  questionNumber += 1;
}

window.addEventListener("keypress", (e) => {
  if (e.key === " ") {
    backDrop.style.transform = "translateY(-100%)";
    input.focus();
  }
});

input.addEventListener("input", (e) => {
  if (e.target.value === "") {
    nextBtn.disabled = true;
  } else {
    nextBtn.disabled = false;
  }
});

function sendToDatabase(input) {
  console.log("Hello");
  fetch("https://cs-project-demo-default-rtdb.firebaseio.com/surveys.json", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      Answer: input,
    }),
  });
}

nextBtn.addEventListener("click", () => {
  if (questions.length < questionNumber) {
    alert("Sorry no more questions!");
  } else {
    sendToDatabase(input.value);
    paraEl.innerText = "";
    input.value = "";
    nextBtn.disabled = true;
    showNextQuestions();
  }
});

showNextQuestions();
