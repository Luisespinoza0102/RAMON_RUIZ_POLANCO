
function openModal(id) { 
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove('hidden');
}

function closeModal(id) { 
    const modal = document.getElementById(id);
    if (modal) modal.classList.add('hidden'); 
}

document.addEventListener('DOMContentLoaded', () => {
    const inputPortada = document.querySelector('input[type="file"]');
    if(inputPortada) {
        inputPortada.id = 'input-portada'; 
        inputPortada.onchange = evt => {
            const [file] = inputPortada.files;
            if (file) {
                const preview = document.getElementById('img-preview');
                const container = document.getElementById('preview-container');
                if (preview) {
                    preview.src = URL.createObjectURL(file);
                    preview.classList.remove('hidden');
                }
                if (container) container.classList.add('opacity-0');
            }
        }
    }
});

async function saveQuick(tipo) {
    let payload = {};

    let url = (tipo === 'autor') ? URL_CREAR_AUTOR : URL_CREAR_GENERO;

    if (tipo === 'autor') {
        const nombre = document.getElementById('inputNombreAutor').value;
        if(!nombre) return alert("El nombre es obligatorio");
        payload = { nombre: nombre };
    } else {
        const nombre = document.getElementById('inputDeweyNom').value;
        const dewey = document.getElementById('inputDeweyCod').value;
        if(!nombre || !dewey) return alert("Ambos campos son obligatorios");
        payload = { nombre: nombre, dewey: dewey };
    }

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN // USAMOS LA CONSTANTE DEL HTML
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.id) {
            const selectId = tipo === 'autor' ? 'id_autores' : 'id_generos';
            const select = document.getElementById(selectId);
            
            if (select) {
                // Creamos la opción y la seleccionamos (true, true)
                const newOption = new Option(data.nombre, data.id, true, true);
                select.add(newOption);
            }
            
            closeModal(tipo === 'autor' ? 'modalAutor' : 'modalDewey');
            
            // Limpiar campos del modal
            if(tipo === 'autor') {
                document.getElementById('inputNombreAutor').value = '';
            } else {
                document.getElementById('inputDeweyNom').value = '';
                document.getElementById('inputDeweyCod').value = '';
            }
        } else {
            alert("Error: " + (data.error || "No se pudo guardar"));
        }
    } catch (error) {
        console.error("Error en la petición:", error);
        alert("Error crítico en el servidor.");
    }
}