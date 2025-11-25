// Community Connect Custom JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Enhanced volunteer signup
    window.volunteerSignup = async function(eventId) {
        try {
            const response = await fetch(`/api/events/${eventId}/volunteer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showNotification('Successfully signed up for the event!', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showNotification('Error: ' + data.error, 'error');
            }
        } catch (error) {
            showNotification('Error signing up for event', 'error');
        }
    };

    // Enhanced cancel signup
    window.cancelVolunteerSignup = async function(eventId) {
        if (!confirm('Are you sure you want to cancel your volunteer signup for this event?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/events/${eventId}/volunteer`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showNotification('Successfully canceled your volunteer signup!', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showNotification('Error: ' + data.error, 'error');
            }
        } catch (error) {
            showNotification('Error canceling volunteer signup', 'error');
        }
    };

    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
        `;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // Event countdown timers
    function updateEventCountdowns() {
        const eventDates = document.querySelectorAll('.event-date');
        eventDates.forEach(element => {
            const eventTime = new Date(element.getAttribute('data-time')).getTime();
            const now = new Date().getTime();
            const distance = eventTime - now;
            
            if (distance > 0) {
                const days = Math.floor(distance / (1000 * 60 * 60 * 24));
                const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                
                element.innerHTML = `Starts in ${days}d ${hours}h`;
            } else {
                element.innerHTML = 'Event completed';
                element.className = 'event-date text-muted';
            }
        });
    }
    
    // Initialize countdowns
    updateEventCountdowns();
    setInterval(updateEventCountdowns, 60000); // Update every minute
});