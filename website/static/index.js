function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function like(sketchId) {
    fetch(`/like-sketch/${sketchId}`, { method: "POST" })
        .then((res) => res.json())
        .then((data) => {
            // Update all heart icons and counts for this sketch (overlay + mobile row)
            document.querySelectorAll(`[data-like-icon="${sketchId}"]`).forEach(el => {
                el.classList.toggle("is-liked", data["liked"]);
            });
            document.querySelectorAll(`[data-likes-count="${sketchId}"]`).forEach(el => {
                el.innerHTML = data["likes"];
            });
        });
}

setTimeout(function() {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        alert.style.transition = "opacity 0.5s ease";
        alert.style.opacity = "0";
        setTimeout(()=> alert.remove(), 500);
    });
}, 3000);

function autoSubmit() {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('sketch_image');

    if (fileInput.files.length > 0) {
        // You could add a loading spinner here if you want!
        form.submit();
    }
}