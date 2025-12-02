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

    // Formatação automática de tags - CORRIGIDO: permite espaços após tags
    tagsInput.addEventListener('input', function(e) {
        let value = this.value;
        let cursorPos = this.selectionStart;
        
        // Se o usuário digitou espaço após uma tag completa (terminada com # ou seguida de espaço/vírgula)
        // Permite o espaço e adiciona # na próxima palavra quando começar a digitar
        if (value.length > 0) {
            // Processa apenas quando o usuário para de digitar (não interfere com espaços)
            const words = value.split(/(\s+)/);
            let processed = [];
            
            for (let i = 0; i < words.length; i++) {
                let word = words[i];
                
                // Se for espaço, mantém
                if (/^\s+$/.test(word)) {
                    processed.push(word);
                    continue;
                }
                
                // Se for vírgula, mantém
                if (word === ',') {
                    processed.push(word);
                    continue;
                }
                
                // Remove # existente para processar
                word = word.replace(/^#+/, '');
                
                // Se a palavra não está vazia e não começa com #, adiciona
                if (word.trim()) {
                    // Se a palavra anterior não terminou com #, adiciona
                    if (processed.length === 0 || !processed[processed.length - 1].endsWith('#')) {
                        processed.push('#' + word.trim());
                    } else {
                        processed.push(word.trim());
                    }
                }
            }
            
            const newValue = processed.join('');
            
            // Só atualiza se mudou significativamente (não apenas espaços)
            if (newValue.replace(/\s/g, '') !== value.replace(/\s/g, '')) {
                this.value = newValue;
                // Restaura posição do cursor
                this.setSelectionRange(cursorPos, cursorPos);
            }
        }
    });
    
    // Processa tags quando o campo perde o foco (formatação final)
    tagsInput.addEventListener('blur', function() {
        let value = this.value;
        // Remove múltiplos espaços, mas mantém espaços entre tags
        value = value.replace(/\s+/g, ' ').trim();
        // Garante que cada palavra comece com #
        value = value.split(' ').map(tag => {
            tag = tag.trim().replace(/^#+/, '');
            return tag ? '#' + tag : '';
        }).filter(tag => tag).join(' ');
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


