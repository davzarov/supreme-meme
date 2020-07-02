$(document).ready(function () {
  $("#dataTable").DataTable({
    emptyTable: "No hay datos",
    //pagingType: 'full',
    language: {
      info: "Viendo _START_ de _END_ hasta _TOTAL_ entradas",
      infoEmpty: "Viendo 0 de 0 hasta 0 entradas",
      lengthMenu: "Viendo _MENU_ entradas",
      loadingRecords: "Cargando...",
      processing: "Procesando...",
      zeroRecords: "No se encontraron resultados",
      search: "Buscar:",
      paginate: {
        first: "Primero",
        previous: "Anterior ",
        next: " Siguiente ",
        last: "Último",
      },
      aria: {
        paginate: {
          first: "First",
          previous: "Previous",
          next: "Next",
          last: "Last",
        },
      },
    },
  });
});
