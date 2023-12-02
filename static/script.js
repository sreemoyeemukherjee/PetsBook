function flagPost(postId) {
        const formId = `#flag-form-${postId}`;
        const formData = new FormData(document.querySelector(formId));

        fetch('/flag-post/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.flagged) {
                document.querySelector(formId + ' button').style.display = 'none';
                document.querySelector(formId + ' label').style.display = 'inline';
            }
        })
        .catch(error => console.error('Error:', error));
    }