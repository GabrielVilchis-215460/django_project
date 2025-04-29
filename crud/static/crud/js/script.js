// for header
document.addEventListener("DOMContentLoaded", function() {
    const userIcon = document.getElementById("userIcon");
    const userMenu = document.getElementById("userMenu")

    userIcon.addEventListener("click", function(e) {
        e.stopPropagation();
        userMenu.style.display = userMenu.style.display == "block" ? "none" : "block";
    });

    document.addEventListener("click", function(e) {
        if (!userMenu.contains(e.target) && !userIcon.contains(e.target)) {
            userMenu.style.display ="none";
        }
    });
});

// for alerts in log out
function showLogoutMessage(event){
    event.preventDefault();
    const isLoggedIn = document.body.classList.contains('logged-in');

    if (isLoggedIn){
        alert('Logout succesfully!')
        window.location.href = event.target.href
    } else {
        alert('No session found. Please log in first.');
    }   
}

// for sidebar
document.addEventListener('DOMContentLoaded', function() {
    const changes = document.querySelectorAll('.filter-toggle');

    changes.forEach(toggle => {
        toggle.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation()

            const list = toggle.nextElementSibling;
            list.classList.toggle('filter-hidden');

            if (list.classList.contains('filter-hidden')){
                toggle.textContent = toggle.textContent.replace('▲','▼');
            } else {
                toggle.textContent = toggle.textContent.replace('▼', '▲');
            }
        });
    });
});

// for increase and decrease products in shopping cart
$(document).ready(function() {
    console.log("Script cargado");

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    $('.qty-btn').click(function() {
        const itemId = $(this).data('id');
        const action = $(this).data('action');

        let url = '';
        if (action === 'increase') {
            url = `/shopping-cart/increment/${itemId}/`;
        } else if (action === 'decrease') {
            url = `/shopping-cart/decrease/${itemId}/`;
        }

        $.ajax({
            url: url,
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            success: function(response) {
                if (response.success) {
                    if (response.quantity > 0) {
                        $('#quantity-' + itemId).text(response.quantity);
                    } else {
                        location.reload();
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error("Error:", error);
            }
        });
    });
});
