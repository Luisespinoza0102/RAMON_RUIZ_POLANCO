document.addEventListener('DOMContentLoaded', function() {
    const tituloInput = document.getElementById('id_titulo');
    const autorSelect = document.getElementById('id_autores');
    const cutterInput = document.getElementById('id_cutter');

    // Función para consultar la API
    async function solicitarCutter() {
        const titulo = tituloInput.value.trim();
        const primerAutorOption = autorSelect.options[autorSelect.selectedIndex];
        const autorNombre = primerAutorOption ? primerAutorOption.text : '';

        if (titulo && autorNombre) {
            try {
                const url = `/catalogo/api/cutter/?autor=${encodeURIComponent(autorNombre)}&titulo=${encodeURIComponent(titulo)}`;
                const response = await fetch(url);
                const data = await response.json();

                if (data.cutter) {
                    cutterInput.value = data.cutter;
                    console.log("Cutter generado:", data.cutter);
                }
            } catch (error) {
                console.error("Error al generar el Cutter:", error);
            }
        }
    }

    // Escuchar eventos de escritura y selección
tituloInput.addEventListener('input', solicitarCutter);
autorSelect.addEventListener('change', solicitarCutter);

const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childlist') {
            solicitarCutter();
        }
    });
});

observer.observe(autorSelect, {childList: true});

});
