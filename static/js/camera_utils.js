document.addEventListener('DOMContentLoaded', () => {
    let stream = null;
    let currentTargetInput = null;

    // --- SELECTOR DINÁMICO ---
    // Esta función busca los elementos cada vez que se necesitan
    const getActiveElements = () => {
        return {
            video: document.getElementById('video-camara') || document.getElementById('video-camera') || document.getElementById('video'),
            canvas: document.getElementById('canvas-foto') || document.getElementById('canvas-camera') || document.getElementById('canvas'),
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
                
                // Ocultar contenedor de preview (el de la nubecita) si existe
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

    function asignarABlobInput(dataURL, input, filename) {
        if (!input || !dataURL) return;
        
        fetch(dataURL)
            .then(res => res.blob())
            .then(blob => {
                const file = new File([blob], filename, { type: "image/jpeg" });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                input.files = dataTransfer.files;
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

    // --- LÓGICA: DOCUMENTOS (GESTIÓN USUARIOS) ---
    document.addEventListener('click', async (e) => {
        const btn = e.target.closest('.btn-activar-camara-doc');
        if (btn) {
            const cod = btn.dataset.cod;
            currentTargetInput = document.getElementById(`file_${cod}`);
            
            const placeholder = document.getElementById('camera-placeholder');
            const container = document.getElementById('camera-container');
            
            if (placeholder) placeholder.classList.add('hidden');
            if (container) container.classList.remove('hidden');

            await iniciarCamara();
        }
    });

    const btnCapturarDoc = document.getElementById('btn-capturar-doc');
    if (btnCapturarDoc) {
        btnCapturarDoc.addEventListener('click', () => {
            const { video, canvas } = getActiveElements();
            const dataURL = capturarYProcesar(video, canvas);
            
            if (currentTargetInput && dataURL) {
                asignarABlobInput(dataURL, currentTargetInput, `doc_usuario.jpg`);
                const cod = currentTargetInput.id.replace('file_', '');
                const status = document.getElementById(`status_${cod}`);
                if (status) { 
                    status.innerText = "¡Listo!"; 
                    status.className = "text-[10px] text-green-400 font-bold"; 
                }
            }
        });
    }
});