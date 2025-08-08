
// Funcionalidad para mensajes flash
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(function(message) {
        // Auto-ocultar después de 5 segundos
        setTimeout(function() {
            hideMessage(message);
        }, 5000);
        
        // Permitir cerrar manualmente
        const closeBtn = message.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                hideMessage(message);
            });
        }
    });
});

// Función para ocultar mensaje con animación
function hideMessage(message) {
    message.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(function() {
        message.remove();
    }, 300);
}
