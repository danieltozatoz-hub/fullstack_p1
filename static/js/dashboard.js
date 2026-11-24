// Lê os dados que a view escreveu na página (json_script) e desenha os gráficos.
// O Django continua sendo o dono dos dados; o Chart.js só desenha.
(function () {
  function ler(id) {
    const el = document.getElementById(id);
    return el ? JSON.parse(el.textContent) : [];
  }

  const cor = '#5c1d14';
  const paleta = ['#5c1d14', '#c0392b', '#2e7d32', '#e0a030'];

  const porMes = ler('dados-mes');
  const canvasMes = document.getElementById('graf-mes');
  if (canvasMes && porMes.length) {
    new Chart(canvasMes, {
      type: 'bar',
      data: {
        labels: porMes.map(d => d.mes),
        datasets: [{ label: 'Empréstimos', data: porMes.map(d => d.total), backgroundColor: cor }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
      },
    });
  }

  const distribuicao = ler('dados-distribuicao');
  const canvasDist = document.getElementById('graf-distribuicao');
  if (canvasDist && distribuicao.some(d => d.total > 0)) {
    new Chart(canvasDist, {
      type: 'doughnut',
      data: {
        labels: distribuicao.map(d => d.situacao),
        datasets: [{ data: distribuicao.map(d => d.total), backgroundColor: paleta }],
      },
      options: { plugins: { legend: { position: 'bottom' } } },
    });
  }
})();
