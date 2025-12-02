// Funcionalidades da página de visualização do sonho

document.addEventListener('DOMContentLoaded', function() {
    const likeBtn = document.querySelector('.like-btn');
    const commentBtn = document.getElementById('toggleComments');
    const favoriteBtn = document.querySelector('.favorite-btn');
    const commentsSection = document.getElementById('commentsSection');
    const commentsList = document.getElementById('commentsList');
    const commentInput = document.getElementById('commentInput');
    const submitComment = document.getElementById('submitComment');

    // Carrega curtidas e favoritos ao carregar página
    loadDreamStats();

    // Funcionalidade de curtir
    if (likeBtn) {
        likeBtn.addEventListener('click', function() {
            const dreamId = this.getAttribute('data-dream-id');
            const isLiked = this.getAttribute('data-liked') === 'true';
            toggleLike(dreamId, !isLiked, this);
        });
    }

    // Funcionalidade de favoritar
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', function() {
            const dreamId = this.getAttribute('data-dream-id');
            const isFavorited = this.getAttribute('data-favorited') === 'true';
            toggleFavorite(dreamId, !isFavorited, this);
        });
    }

    // Toggle comentários
    if (commentBtn) {
        commentBtn.addEventListener('click', function() {
            commentsSection.style.display = commentsSection.style.display === 'none' ? 'block' : 'none';
            if (commentsSection.style.display === 'block') {
                loadComments();
            }
        });
    }

    // Enviar comentário
    if (submitComment) {
        submitComment.addEventListener('click', function() {
            const dreamId = this.getAttribute('data-dream-id');
            const content = commentInput.value.trim();
            
            if (!content) {
                alert('Por favor, escreva um comentário.');
                return;
            }

            fetch('/api/comment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ dream_id: dreamId, content: content })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    commentInput.value = '';
                    loadComments();
                } else {
                    alert('Erro ao comentar: ' + (data.error || 'Erro desconhecido'));
                }
            })
            .catch(error => {
                console.error('Erro ao comentar:', error);
                alert('Erro ao comentar. Tente novamente.');
            });
        });
    }

    function loadDreamStats() {
        const dreamId = likeBtn?.getAttribute('data-dream-id');
        if (!dreamId) return;

        // Carrega estatísticas (curtidas, favoritos)
        fetch(`/api/dream-stats/${dreamId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (likeBtn) {
                        likeBtn.setAttribute('data-liked', data.is_liked ? 'true' : 'false');
                        const icon = likeBtn.querySelector('i');
                        const countSpan = likeBtn.querySelector('.like-count');
                        
                        if (data.is_liked) {
                            likeBtn.classList.add('liked');
                            icon.className = 'bi bi-heart-fill';
                        }
                        if (countSpan) {
                            countSpan.textContent = data.like_count || 0;
                        }
                    }
                    
                    if (favoriteBtn) {
                        favoriteBtn.setAttribute('data-favorited', data.is_favorited ? 'true' : 'false');
                        const icon = favoriteBtn.querySelector('i');
                        if (data.is_favorited) {
                            favoriteBtn.classList.add('favorited');
                            icon.className = 'bi bi-bookmark-fill';
                        }
                    }
                }
            })
            .catch(error => console.error('Erro ao carregar estatísticas:', error));
    }

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
        .catch(error => console.error('Erro ao curtir:', error));
    }

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
                } else {
                    button.classList.remove('favorited');
                    button.setAttribute('data-favorited', 'false');
                    icon.className = 'bi bi-bookmark';
                }
            }
        })
        .catch(error => console.error('Erro ao favoritar:', error));
    }

    function loadComments() {
        const dreamId = likeBtn?.getAttribute('data-dream-id');
        if (!dreamId) return;

        fetch(`/api/comments/${dreamId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.comments.length === 0) {
                        commentsList.innerHTML = '<p style="color: #888; text-align: center; padding: 2rem;">Nenhum comentário ainda. Seja o primeiro!</p>';
                    } else {
                        commentsList.innerHTML = data.comments.map(comment => `
                            <div class="comment-item">
                                <div class="comment-author">
                                    ${comment.picture ? 
                                        `<img src="${comment.picture}" alt="${comment.name}" class="comment-avatar">` :
                                        `<div class="comment-avatar-placeholder"><i class="bi bi-person-circle"></i></div>`
                                    }
                                    <div class="comment-author-info">
                                        <strong>${comment.name || comment.username}</strong>
                                        <span class="comment-date">${new Date(comment.created_at).toLocaleString('pt-BR')}</span>
                                    </div>
                                </div>
                                <div class="comment-content">${comment.content.replace(/\n/g, '<br>')}</div>
                            </div>
                        `).join('');
                    }
                }
            })
            .catch(error => {
                console.error('Erro ao carregar comentários:', error);
                commentsList.innerHTML = '<p style="color: #ff4444;">Erro ao carregar comentários.</p>';
            });
    }
});
