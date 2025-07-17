document.addEventListener("DOMContentLoaded", function () {
    const container = document.querySelector('.container0');
    const registerBtn = document.querySelector('.register-btn');
    const loginBtn = document.querySelector('.login-btn');
    const loginForm = document.querySelector(".form-box.login form");
    const registerForm = document.querySelector(".form-box.register form");
    const flashModal = document.getElementById("flashModal"); 
    const flashMessage = document.getElementById("flashMessage");

    if (registerBtn && loginBtn) {
        registerBtn.addEventListener('click', () => container.classList.add('active'));
        loginBtn.addEventListener('click', () => container.classList.remove('active'));
    } else {
        console.error("registerBtn or loginBtn not found in DOM!");
    }

    // Update your login form handler
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = {
        username: this.username.value,
        password: this.password.value
    };

    fetch('/form/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        const modal = document.getElementById('notificationModal');
        const modalBody = modal.querySelector('.modal-body');
        
        // Update modal content
        modalBody.textContent = data.message;
        
        // Show modal
        $('#notificationModal').modal('show');
        
        // Redirect after delay if successful
        if (data.redirect) {
            setTimeout(() => {
                window.location.href = data.redirect;
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
    document.querySelector('#registerForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            username: this.username.value,
            email: this.email.value,
            password: this.password.value
        };
    
        console.log("Sending registration data:", formData);
    
        fetch('/form/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            showMessage(data.message, 'success');
            if (data.redirect) {
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 2000);
            }
        })
        .catch(error => {
            console.error('Registration error:', error);
            showMessage(error.message || 'Registration failed!', 'danger');
        });
    });
    
    
    
    function showMessage(text, type) {
        const messageDiv = document.getElementById('messageContainer');
        messageDiv.textContent = text;
        messageDiv.className = `alert alert-${type}`;
        messageDiv.style.display = 'block';
        
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
});
