document.getElementById('exercise-form').reset();
document.getElementById("submit-btn").addEventListener("click", (e) => {
    const btn = e.target;
    const form = document.getElementById("exercise-form");
    const inputs = form.querySelectorAll("input[id]");
    const csrfToken = document.querySelector("input[name=csrf_token]").value;
    const answers = {};

    let allFilled = true;
    inputs.forEach(input => {
        answers[input.id] = input.value;
        if (!input.value.trim()) {
            allFilled = false;
        }
    });

    if (!allFilled) {
        console.log("All values aren't full!")
        btn.classList.add("cursor-not-allowed")
        btn.classList.add("bg-red-400")
        setTimeout(() => {
            btn.classList.remove("bg-red-400");
            btn.classList.remove("cursor-not-allowed");
        }, 1000);
        return;
    }

    btn.disabled = true;
    btn.classList.add("cursor-not-allowed");
    btn.classList.add("bg-slate-500");

    fetch(`${window.location.pathname}/submit`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify(answers)
    })
        .then(res => res.json())
        .then(data => {
            console.log(data); // Handle result
            Object.entries(data).forEach(([key, isCorrect]) => {
                const input = document.getElementById(key);
                if (input) {
                    input.classList.remove("bg-green-500", "bg-red-400");
                    if (isCorrect) {
                        input.classList.add("bg-green-500");
                    } else {
                        input.classList.add("bg-red-400");
                    }
                }
            });
        });
});
