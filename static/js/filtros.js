// Manejo de Filtros
function selectFilter(filterName) {
    const input = document.getElementById('filterInput');
    if (!input) return;
    
    input.value = filterName;

    const tabs = document.querySelectorAll('.filter-tab');
    tabs.forEach(tab => {
        tab.classList.remove('bg-blue-600', 'text-white', 'shadow-md', 'border-transparent');
        tab.classList.add('text-gray-600', 'bg-white', 'border-gray-200');
        
        if(tab.dataset.filter === filterName) {
            tab.classList.remove('text-gray-600', 'bg-white', 'border-gray-200');
            tab.classList.add('bg-blue-600', 'text-white', 'shadow-md', 'border-transparent');
        }
    });

    const searchInput = document.getElementById('searchInput');
    const placeholders = {
        'titulo': 'Buscar por Título...',
        'cutter': 'Buscar por código Cutter...',
        'autor': 'Buscar por nombre del Autor...',
        'genero': 'Buscar por Género o Código Dewey...',
        'estante': 'Buscar por ubicación/Estante...'
    };
    searchInput.placeholder = placeholders[filterName] || 'Buscar...';
    searchInput.focus();
}

// Función para confirmar eliminación
function confirmarEliminacion(libroId, titulo) {
    // Usamos una confirmación nativa sencilla, o podrías usar SweetAlert2 después
    const mensaje = `¿Estás seguro de eliminar "${titulo}"?\n\nEsta acción borrará TODOS los ejemplares asociados y no se puede deshacer.`;
    
    if (confirm(mensaje)) {
        document.getElementById(`delete-form-${libroId}`).submit();
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    const filterInput = document.getElementById('filterInput');
    if (filterInput) {
        const currentFilter = filterInput.value || 'titulo';
        selectFilter(currentFilter);
    }
});