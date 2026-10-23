// Plugins jQuery usados em todo o site: Bootbox (confirmações) e jQuery Mask (máscaras).
$(function () {
  // Confirmação com Bootbox: <form data-confirmar="Mensagem" data-confirmar-titulo="..." data-confirmar-botao="...">
  $(document).on('submit', 'form[data-confirmar]', function (e) {
    const form = this;
    if (form.dataset.confirmado) return;
    e.preventDefault();
    bootbox.confirm({
      title: form.dataset.confirmarTitulo || 'Confirmar',
      // .text() escapa o conteúdo: a mensagem pode trazer nomes digitados por usuários
      message: $('<p class="mb-0">').text(form.dataset.confirmar),
      buttons: {
        cancel: { label: 'Cancelar', className: 'btn-secondary' },
        confirm: { label: form.dataset.confirmarBotao || 'Confirmar', className: 'btn-danger' },
      },
      callback: function (ok) {
        if (!ok) return;
        form.dataset.confirmado = '1';
        form.submit();
      },
    });
  });

  // Máscaras com jQuery Mask
  $('.mascara-preco').mask('#########0.00', { reverse: true });
  $('.mascara-inteiro').mask('#########0');
});
