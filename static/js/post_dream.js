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

    // Formatação automática de tags
    tagsInput.addEventListener('input', function() {
        let value = this.value;
        // Remove múltiplos espaços e vírgulas
        value = value.replace(/[,\s]+/g, ' ');
        // Adiciona # no início de palavras que não têm
        value = value.split(' ').map(tag => {
            tag = tag.trim();
            if (tag && !tag.startsWith('#')) {
                return '#' + tag;
            }
            return tag;
        }).filter(tag => tag).join(' ');
        
        if (value !== this.value) {
            this.value = value;
        }
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

    // Inicializa progresso
    updateProgress();
});

