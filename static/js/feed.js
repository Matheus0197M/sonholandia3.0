// Funcionalidades do feed: expansão de sonhos, menu, curtidas, favoritos, busca

document.addEventListener('DOMContentLoaded', function() {
    // Menu Dropdown
    const menuButton = document.getElementById('menuButton');
    const menuDropdown = document.getElementById('menuDropdown');
    
    if (menuButton && menuDropdown) {
        menuButton.addEventListener('click', function(e) {
            e.stopPropagation();
            menuDropdown.classList.toggle('active');
        });
        
        // Fecha menu ao clicar fora
        document.addEventListener('click', function(e) {
            if (!menuButton.contains(e.target) && !menuDropdown.contains(e.target)) {
                menuDropdown.classList.remove('active');
            }
        });
    }
    
    // Expansão de Sonhos
    const expandButtons = document.querySelectorAll('.expand-dream-btn');
    
    expandButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const dreamId = this.getAttribute('data-dream-id');
            if (!dreamId) return;
            
            const dreamCard = document.querySelector(`.dream-card[data-dream-id="${dreamId}"]`);
            
            if (!dreamCard) {
                console.error('Card do sonho não encontrado:', dreamId);
                // Redireciona para página completa se o card não for encontrado
                window.location.href = `/sonho/${dreamId}`;
                return;
            }
            
            const preview = dreamCard.querySelector('.dream-preview');
            const full = dreamCard.querySelector('.dream-full');
            
            if (!preview || !full) {
                console.error('Elementos do card não encontrados');
                return;
            }
            
            if (dreamCard.classList.contains('expanded')) {
                // Recolhe
                dreamCard.classList.remove('expanded');
                full.style.display = 'none';
                preview.style.display = 'block';
            } else {
                // Expande
                if (!full.hasAttribute('data-loaded')) {
                    // Carrega conteúdo completo via AJAX
                    loadDreamFull(dreamId, full, dreamCard, preview);
                } else {
                    full.style.display = 'block';
                    preview.style.display = 'none';
                }
                dreamCard.classList.add('expanded');
                
                // Scroll suave para o sonho expandido
                setTimeout(() => {
                    dreamCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            }
        });
    });
    
    // Função para carregar conteúdo completo do sonho
    function loadDreamFull(dreamId, container, dreamCard, preview) {
        container.innerHTML = '<div style="text-align: center; padding: 2rem;"><i class="bi bi-hourglass-split" style="font-size: 2rem; color: #029ce4;"></i><p>Carregando...</p></div>';
        container.style.display = 'block';
        preview.style.display = 'none';
        
        fetch(`/sonho/${dreamId}/json`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.dream) {
                    let html = '';
                    
                    // Título completo
                    html += `<h2 class="dream-full-title">${data.dream.title}</h2>`;
                    
                    // Imagem completa se houver
                    if (data.dream.image_path) {
                        const imagePath = data.dream.image_path.startsWith('/static/') ? data.dream.image_path : '/static/' + data.dream.image_path;
                        html += `<div class="dream-full-image"><img src="${imagePath}" alt="${data.dream.title}" /></div>`;
                    }
                    
                    // Descrição completa
                    html += `<div class="dream-full-content">${data.dream.description.replace(/\n/g, '<br>')}</div>`;
                    
                    // Tags se houver
                    if (data.tags && data.tags.length > 0) {
                        html += '<div class="dream-tags-full">';
                        data.tags.forEach(tag => {
                            html += `<a href="/feed?tag=${encodeURIComponent(tag)}" class="tagsEngajamento">#${tag}</a>`;
                        });
                        html += '</div>';
                    }
                    
                    // Botão para ver página completa
                    html += `<div style="margin-top: 1rem; text-align: center;"><a href="/sonho/${dreamId}" class="verMaisDentro">Ver página completa</a></div>`;
                    
                    container.innerHTML = html;
                    container.setAttribute('data-loaded', 'true');
                    
                    // Registra no histórico
                    registerHistory(dreamId, 'view');
                } else {
                    container.innerHTML = '<p style="color: #ff4444; padding: 2rem; text-align: center;">Erro ao carregar sonho. <a href="/sonho/' + dreamId + '">Tentar página completa</a></p>';
                    preview.style.display = 'block';
                    container.style.display = 'none';
                    dreamCard.classList.remove('expanded');
                }
            })
            .catch(error => {
                console.error('Erro ao carregar sonho:', error);
                container.innerHTML = '<p style="color: #ff4444; padding: 2rem; text-align: center;">Erro ao carregar sonho. <a href="/sonho/' + dreamId + '">Clique aqui para ver a página completa</a></p>';
                preview.style.display = 'block';
                container.style.display = 'none';
                dreamCard.classList.remove('expanded');
            });
    }
    
    // Sistema de Curtidas
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const dreamId = this.getAttribute('data-dream-id');
            const isLiked = this.getAttribute('data-liked') === 'true';
            
            toggleLike(dreamId, !isLiked, this);
        });
    });
    
    function toggleLike(dreamId, like, button) {
        fetch('/api/like', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ dream_id: dreamId, like: like })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const icon = button.querySelector('i');
                const countSpan = button.querySelector('.like-count');
                
                if (like) {
                    button.classList.add('liked');
                    button.setAttribute('data-liked', 'true');
                    icon.className = 'bi bi-heart-fill';
                    registerHistory(dreamId, 'like');
                } else {
                    button.classList.remove('liked');
                    button.setAttribute('data-liked', 'false');
                    icon.className = 'bi bi-heart';
                }
                
                if (countSpan) {
                    countSpan.textContent = data.like_count || 0;
                }
            }
        })
        .catch(error => {
            console.error('Erro ao curtir:', error);
        });
    }
    
    // Sistema de Favoritos
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const dreamId = this.getAttribute('data-dream-id');
            const isFavorited = this.getAttribute('data-favorited') === 'true';
            
            toggleFavorite(dreamId, !isFavorited, this);
        });
    });
    
    function toggleFavorite(dreamId, favorite, button) {
        fetch('/api/favorite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ dream_id: dreamId, favorite: favorite })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const icon = button.querySelector('i');
                
                if (favorite) {
                    button.classList.add('favorited');
                    button.setAttribute('data-favorited', 'true');
                    icon.className = 'bi bi-bookmark-fill';
                    registerHistory(dreamId, 'favorite');
                } else {
                    button.classList.remove('favorited');
                    button.setAttribute('data-favorited', 'false');
                    icon.className = 'bi bi-bookmark';
                }
            }
        })
        .catch(error => {
            console.error('Erro ao favoritar:', error);
        });
    }
    
    // Registro de Histórico
    function registerHistory(dreamId, actionType) {
        fetch('/api/history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ dream_id: dreamId, action_type: actionType })
        })
        .catch(error => console.error('Erro ao registrar histórico:', error));
    }
    
    // Sistema de Significados de Sonhos
    const meaningButtons = document.querySelectorAll('.meaning-btn');
    meaningButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const dreamId = this.getAttribute('data-dream-id');
            toggleDreamMeaning(dreamId, this);
        });
    });
    
    function toggleDreamMeaning(dreamId, button) {
        const dreamCard = document.querySelector(`.dream-card[data-dream-id="${dreamId}"]`);
        if (!dreamCard) return;
        
        let meaningDiv = dreamCard.querySelector('.dream-meanings-container');
        
        if (meaningDiv && meaningDiv.style.display !== 'none') {
            // Fecha significados
            meaningDiv.style.display = 'none';
            button.classList.remove('active');
        } else {
            // Abre significados
            if (!meaningDiv) {
                // Cria container
                meaningDiv = document.createElement('div');
                meaningDiv.className = 'dream-meanings-container';
                meaningDiv.innerHTML = '<div style="padding: 1rem; text-align: center;"><i class="bi bi-hourglass-split"></i> Buscando significados...</div>';
                dreamCard.appendChild(meaningDiv);
            }
            
            meaningDiv.style.display = 'block';
            button.classList.add('active');
            
            // Busca significados da API
            fetch(`/api/dream-meaning/${dreamId}?lang=pt`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.meanings && data.meanings.length > 0) {
                        let html = '<div class="meanings-list" style="padding: 1rem;">';
                        html += '<h4 style="margin-top: 0; color: #667eea;">Significados Encontrados:</h4>';
                        
                        data.meanings.forEach(m => {
                            html += `<div class="meaning-item" style="margin: 0.8rem 0; padding: 0.8rem; background: #f5f5f5; border-left: 4px solid #667eea; border-radius: 4px; color: #000;">`;
                            html += `<strong>#${m.word}</strong><br>`;
                            html += `<small>${m.meaning}</small><br>`;
                            html += `<small style="color: #999;">Fonte: ${m.source}</small>`;
                            html += `</div>`;
                        });
                        
                        html += '</div>';
                        meaningDiv.innerHTML = html;
                    } else {
                        meaningDiv.innerHTML = '<div style="padding: 1rem; color: #ff6b6b;">Nenhum significado encontrado para este sonho.</div>';
                    }
                })
                .catch(error => {
                    console.error('Erro ao buscar significados:', error);
                    meaningDiv.innerHTML = '<div style="padding: 1rem; color: #ff6b6b;">Erro ao carregar significados.</div>';
                });
        }
    }
    
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 500);
            } else if (query.length === 0) {
                // Recarrega feed completo
                window.location.href = '/feed';
            }
        });
    }
    
    function performSearch(query) {
        // Implementação de busca será feita no backend
        window.location.href = `/feed?search=${encodeURIComponent(query)}`;
    }
    
    // Mantém função original de reveal
    revealOnScroll();
});

function revealOnScroll() {
    const reveals = document.querySelectorAll(".reveal");
    for(let el of reveals) {
       const windowHeight = window.innerHeight;
       const elementTop = el.getBoundingClientRect().top;
       const elementBottom = el.getBoundingClientRect().bottom;

       if (elementTop < windowHeight - 100 && elementBottom > 100) {
           el.classList.add("active");
       } else {
           el.classList.remove("active");
       }
    }   
}

window.addEventListener("scroll", revealOnScroll);
window.addEventListener("load", revealOnScroll);
