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
    const expandButtons = document.querySelectorAll('.expand-dream-btn, .expand-dream');
    
    expandButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const dreamId = this.getAttribute('data-dream-id');
            const dreamCard = document.querySelector(`.dream-card[data-dream-id="${dreamId}"]`);
            
            if (!dreamCard) return;
            
            const preview = dreamCard.querySelector('.dream-preview');
            const full = dreamCard.querySelector('.dream-full');
            
            if (dreamCard.classList.contains('expanded')) {
                // Recolhe
                dreamCard.classList.remove('expanded');
                full.style.display = 'none';
                preview.style.display = 'block';
            } else {
                // Expande
                if (!full.hasAttribute('data-loaded')) {
                    // Carrega conteúdo completo via AJAX
                    loadDreamFull(dreamId, full);
                } else {
                    full.style.display = 'block';
                }
                dreamCard.classList.add('expanded');
                preview.style.display = 'none';
                
                // Scroll suave para o sonho expandido
                dreamCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // Função para carregar conteúdo completo do sonho
    function loadDreamFull(dreamId, container) {
        container.innerHTML = '<div style="text-align: center; padding: 2rem;"><i class="bi bi-hourglass-split" style="font-size: 2rem; color: #029ce4;"></i><p>Carregando...</p></div>';
        
        fetch(`/sonho/${dreamId}/json`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let html = '';
                    
                    if (data.dream.image_path) {
                        html += `<div class="dream-full-image"><img src="/static/${data.dream.image_path}" alt="${data.dream.title}" /></div>`;
                    }
                    
                    html += `<div class="dream-full-content">${data.dream.description.replace(/\n/g, '<br>')}</div>`;
                    
                    if (data.tags && data.tags.length > 0) {
                        html += '<div class="dream-tags-full">';
                        data.tags.forEach(tag => {
                            html += `<a href="/feed?tag=${tag}" class="tagsEngajamento">#${tag}</a>`;
                        });
                        html += '</div>';
                    }
                    
                    container.innerHTML = html;
                    container.setAttribute('data-loaded', 'true');
                    
                    // Registra no histórico
                    registerHistory(dreamId, 'view');
                } else {
                    container.innerHTML = '<p style="color: #ff4444;">Erro ao carregar sonho.</p>';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar sonho:', error);
                container.innerHTML = '<p style="color: #ff4444;">Erro ao carregar sonho.</p>';
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
    
    // Sistema de Busca
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
