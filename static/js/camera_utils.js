document.addEventListener('DOMContentLoaded', () => {
    let stream = null;
    let currentTargetInput = null;

    // --- SELECTOR DINÁMICO DE ELEMENTOS ---
    const getActiveElements = () => {
        return {
            video: document.getElementById('video-camara') || document.getElementById('video-camera') || document.getElementById('video'),
            canvas: document.getElementById('canvas-foto') || document.getElementById('canvas-camera') || document.getElementById('canvas'),
            // Detecta tanto el contenedor del modal como el de la sección de edición
            docContainer: document.getElementById('camera-container') || document.getElementById('camera-section')
        };
    };

    // --- FUNCIONES CORE ---
    async function iniciarCamara(preview = null, btnIni = null, btnCap = null) {
        const { video } = getActiveElements();

        if (!video) {
            console.error("Error: No se encontró el elemento <video> en el HTML.");
            return;
        }

        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: "environment" } 
            });
            
            video.srcObject = stream;
            
            video.onloadedmetadata = () => {
                video.play();
                video.classList.remove('hidden');
                
                const previewContainer = document.getElementById('preview-container');
                if (previewContainer) previewContainer.classList.add('hidden');
            };

            if (preview) preview.classList.add('hidden');
            if (btnIni) btnIni.classList.add('hidden');
            if (btnCap) btnCap.classList.remove('hidden');

        } catch (err) {
            console.error("Error acceso cámara:", err);
            alert("No se pudo acceder a la cámara. Verifica los permisos o usa HTTPS.");
        }
    }

    function detenerCamara() {
        const { video } = getActiveElements();
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            if (video) video.srcObject = null;
            stream = null;
        }
    }

    function capturarYProcesar(v, c, prev = null) {
        if (!v || !c) return null;
        
        c.width = v.videoWidth;
        c.height = v.videoHeight;
        const context = c.getContext('2d');
        context.drawImage(v, 0, 0, c.width, c.height);
        
        const dataURL = c.toDataURL('image/jpeg');
        
        if (prev) {
            prev.src = dataURL;
            prev.classList.remove('hidden');
            v.classList.add('hidden');
        }
        return dataURL;
    }

    function actualizarLabelEstado(inputElement, mensaje, esExito = true) {
        if (!inputElement) return;
        
        // Extrae el código del documento del ID (funciona para file_new_COD o file_COD)
        const esModal = inputElement.id.startsWith('file_new_');
        const cod = esModal ? inputElement.id.replace('file_new_', '') : inputElement.id.replace('file_', '');
        
        // Intenta buscar el elemento de estado en el modal o en la vista edición
        const statusLabel = document.getElementById(`status_new_${cod}`) || document.getElementById(`status_${cod}`);
        
        if (statusLabel) {
            statusLabel.innerText = mensaje;
            statusLabel.className = esExito 
                ? "text-[10px] text-green-400 font-bold uppercase tracking-wider block max-w-[180px] truncate"
                : "text-[10px] text-slate-500 font-mono italic block";
        }
    }

    function asignarABlobInput(dataURL, input, filename) {
        if (!input || !dataURL) return;
        
        fetch(dataURL)
            .then(res => res.blob())
            .then(blob => {
                const file = new File([blob], filename, { type: "image/jpeg" });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                input.files = dataTransfer.files;

                // Despacha un evento de cambio artificial para que los listeners de actualización lo detecten
                input.dispatchEvent(new Event('change', { bubbles: true }));
            });
    }

    // --- LÓGICA: PORTADA DE LIBROS ---
    const btnIniciarPortada = document.getElementById('btn-iniciar-camara');
    const btnCapturarPortada = document.getElementById('btn-capturar');
    const inputPortada = document.getElementById('input-portada') || document.querySelector('input[name="imagen_portada"]');
    const previewPortada = document.getElementById('img-preview');

    if (btnIniciarPortada) {
        btnIniciarPortada.addEventListener('click', () => {
            iniciarCamara(previewPortada, btnIniciarPortada, btnCapturarPortada);
        });
    }

    if (btnCapturarPortada) {
        btnCapturarPortada.addEventListener('click', () => {
            const { video, canvas } = getActiveElements();
            const dataURL = capturarYProcesar(video, canvas, previewPortada);
            
            if (dataURL && inputPortada) {
                asignarABlobInput(dataURL, inputPortada, "portada.jpg");
                detenerCamara();
                btnCapturarPortada.classList.add('hidden');
                btnIniciarPortada.classList.remove('hidden');
            }
        });
    }

    // --- LÓGICA: DOCUMENTOS (GESTIÓN Y EDICIÓN USUARIOS) ---
    
    // Captura el clic del botón de activación para saber qué input cargar
    document.addEventListener('click', async (e) => {
        const btn = e.target.closest('.btn-activar-camara-doc');
        if (btn) {
            const cod = btn.dataset.cod;
            const { docContainer } = getActiveElements();
            
            // Busca el input ya sea en el modal de registro o en la vista de edición
            currentTargetInput = document.getElementById(`file_new_${cod}`) || document.getElementById(`file_${cod}`);
            
            const placeholder = document.getElementById('camera-placeholder');
            if (placeholder) placeholder.classList.add('hidden');
            if (docContainer) docContainer.classList.remove('hidden');

            await iniciarCamara();
        }
    });

    // Acción del botón capturar para documentos
    const btnCapturarDoc = document.getElementById('btn-capturar-doc');
    if (btnCapturarDoc) {
        btnCapturarDoc.addEventListener('click', () => {
            const { video, canvas, docContainer } = getActiveElements();
            const dataURL = capturarYProcesar(video, canvas);
            
            if (currentTargetInput && dataURL) {
                const esModal = currentTargetInput.id.startsWith('file_new_');
                const cod = esModal ? currentTargetInput.id.replace('file_new_', '') : currentTargetInput.id.replace('file_', '');
                
                asignarABlobInput(dataURL, currentTargetInput, `captura_${cod}.jpg`);
                
                detenerCamara();
                if (docContainer) docContainer.classList.add('hidden');
            }
        });
    }

    // Escucha global de inputs de tipo archivo para inyectar dinámicamente el nombre o feedback visual
    document.addEventListener('change', (e) => {
        const input = e.target;
        if (input.tagName === 'INPUT' && input.type === 'file' && (input.id.startsWith('file_new_') || input.id.startsWith('file_'))) {
            if (input.files && input.files.length > 0) {
                const nombreArchivo = input.files[0].name;
                // Si el nombre es genérico del blob, le damos un mejor aspecto visual
                const textoVisual = nombreArchivo.startsWith('captura_') ? "✓ FOTO CAPTURADA" : `✓ ${nombreArchivo}`;
                actualizarLabelEstado(input, textoVisual, true);
            } else {
                actualizarLabelEstado(input, "Pendiente", false);
            }
        }
    });
});