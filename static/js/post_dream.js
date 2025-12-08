// Barra de progresso e validação do formulário de postagem

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('dreamForm');
    const titleInput = document.getElementById('title');
    const descriptionInput = document.getElementById('description');
    const dreamTypeSelect = document.getElementById('dream_type');
    const tagsInput = document.getElementById('tags');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const charCount = document.getElementById('charCount');
    const submitBtn = document.getElementById('submitBtn');

    // Atualiza contador de caracteres
    descriptionInput.addEventListener('input', function() {
        const count = this.value.length;
        charCount.textContent = count;
        
        if (count > 4500) {
            charCount.style.color = '#ff4444';
        } else if (count > 4000) {
            charCount.style.color = '#ffa500';
        } else {
            charCount.style.color = '#888';
        }
        
        updateProgress();
    });

    // Atualiza barra de progresso
    function updateProgress() {
        let filled = 0;
        const total = 4; // título, descrição, tipo, tags (opcional)

        if (titleInput.value.trim()) filled++;
        if (descriptionInput.value.trim()) filled++;
        if (dreamTypeSelect.value) filled++;
        // Tags são opcionais, mas contam se preenchidas
        if (tagsInput.value.trim()) filled++;

        const percentage = (filled / total) * 100;
        progressFill.style.width = percentage + '%';
        progressText.textContent = Math.round(percentage) + '%';
    }

    // Adiciona listeners para atualizar progresso
    titleInput.addEventListener('input', updateProgress);
    dreamTypeSelect.addEventListener('change', updateProgress);
    tagsInput.addEventListener('input', updateProgress);

    // Formatação de tags - SEM interferência no input (sem movimento de cursor)
    // A formatação final ocorre apenas no blur (quando sai do campo)
    tagsInput.addEventListener('blur', function() {
        let value = this.value.trim();
        if (!value) return;
        
        // Substitui vírgulas por espaços para normalização
        value = value.replace(/,/g, ' ');
        
        // Remove # existentes (vamos adicionar de forma consistente)
        value = value.replace(/#/g, '');
        
        // Divide por espaços e filtra vazios
        let tags = value.split(/\s+/).filter(tag => tag.length > 0);
        
        // Reconstrói com # no início de cada tag
        value = tags.map(tag => '#' + tag.toLowerCase()).join(' ');
        
        this.value = value;
    });

    // Validação antes de enviar
    form.addEventListener('submit', function(e) {
        const title = titleInput.value.trim();
        const description = descriptionInput.value.trim();
        const dreamType = dreamTypeSelect.value;

        if (!title || !description || !dreamType) {
            e.preventDefault();
            alert('Por favor, preencha todos os campos obrigatórios.');
            return false;
        }

        if (description.length < 10) {
            e.preventDefault();
            alert('A descrição deve ter pelo menos 10 caracteres.');
            return false;
        }

        // Desabilita botão durante envio
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Enviando...';
    });

    // Preview de imagem
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('imagePreview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    alert('A imagem deve ter no máximo 5MB.');
                    this.value = '';
                    imagePreview.classList.remove('active');
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                    imagePreview.classList.add('active');
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.classList.remove('active');
            }
        });
    }

    // Inicializa progresso
    updateProgress();
});


