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
        btn.classList.remove("button-blue");
        btn.classList.add("button-red-disabled");
        btn.disabled = true
        setTimeout(() => {
            btn.classList.remove("button-red-disabled");
            btn.classList.add("button-blue");
            btn.disabled = false
        }, 1000);
        return;
    }

    btn.disabled = true;
    btn.classList.remove("button-red");
    btn.classList.add("button-red-disabled");

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
document.getElementById("reveal-btn").addEventListener("click", async (e) => {
    const btn = e.target;
    const btn2 = document.getElementById("submit-btn")
    const inputs = form.querySelectorAll("input[id]");
    const res = await fetch(`${window.location.href}/answers`)
    const answers = await res.json();

    btn.disabled = true
    btn.classList.remove("button-red")
    btn.classList.add("button-red-disabled")
    btn2.disabled = true
    btn2.classList.remove("button-blue")
    btn2.classList.add("button-red-disabled")

    Object.entries(answers).forEach(([key, value]) => {
        const input = document.getElementById(key);
        if (input) {
            input.classList.remove("bg-green-500", "bg-red-400");
            input.readonly = true
            input.value = value[0]
            input.classList.add("bg-green-500");
        }
    });
});