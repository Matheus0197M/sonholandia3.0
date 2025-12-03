// Verificação periódica se o sonho foi processado

document.addEventListener('DOMContentLoaded', function() {
    const loadingFill = document.getElementById('loadingFill');
    const loadingStatus = document.getElementById('loadingStatus');
    
    let progress = 0;
    let checkInterval;
    let progressInterval;

    // Simula progresso da barra de carregamento
    function simulateProgress() {
        progressInterval = setInterval(function() {
            if (progress < 90) {
                progress += Math.random() * 10;
                if (progress > 90) progress = 90;
                loadingFill.style.width = progress + '%';
            }
        }, 500);
    }

    // Verifica se o sonho está pronto
    function checkDreamReady() {
        fetch(checkUrl)
            .then(response => response.json())
            .then(data => {
                if (data.ready) {
                    // Sonho está pronto
                    clearInterval(checkInterval);
                    clearInterval(progressInterval);
                    
                    loadingFill.style.width = '100%';
                    loadingStatus.textContent = 'Sonho processado com sucesso!';
                    
                    // Redireciona após 1 segundo
                    setTimeout(function() {
                        window.location.href = viewUrl;
                    }, 1000);
                } else {
                    // Continua verificando
                    loadingStatus.textContent = 'Verificando informações...';
                }
            })
            .catch(error => {
                console.error('Erro ao verificar sonho:', error);
                loadingStatus.textContent = 'Erro ao verificar. Tentando novamente...';
            });
    }

    // Inicia verificação periódica
    simulateProgress();
    
    // Verifica a cada 2 segundos
    checkInterval = setInterval(checkDreamReady, 2000);
    
    // Primeira verificação imediata
    checkDreamReady();

    // Atualiza status durante o carregamento
    const statusMessages = [
        'Salvando informações...',
        'Processando tags...',
        'Organizando dados...',
        'Finalizando...'
    ];
    
    let statusIndex = 0;
    setInterval(function() {
        if (progress < 90) {
            loadingStatus.textContent = statusMessages[statusIndex % statusMessages.length];
            statusIndex++;
        }
    }, 2000);
});




