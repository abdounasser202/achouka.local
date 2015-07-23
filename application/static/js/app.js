/**
 * Created by wilrona on 15/04/2015.
 */

$(document).ready(function() {

   // Google styled selects
    $("select.g-select").each(function() {
        var e = $(this)
        e.select2()
    })

    $('#datepicker').datepicker({
        format: "dd/mm/yyyy",
        weekStart: 1,
        todayBtn: "linked",
        autoclose: true,
        orientation: "top auto",
        todayHighlight: true
    });
    /*
    $('#datepickerbirth').datepicker({
        format: "dd/mm/yyyy",
        startView: 2,
        weekStart: 1,
        autoclose: true,
        orientation: "top auto",
        clearbtn: true
    }); */

    $('#datepickerbirth').inputmask("date", { placeholder:"__/__/____"})


    $('#datepickeryear').datepicker({
        format: "yyyy",
        startView: 1,
        minViewMode: 2,
        autoclose: true,
        orientation: "top auto",
        clearbtn: true
    });

    $('#datetimepicker2').datetimepicker({
        format: "LT",
        locale: "fr",
        useCurrent: false
    });

    $('#datetimepicker1').datetimepicker({
        format: "LT",
        locale: "fr",
        useCurrent: false
    });

    $('#myModal').on('hide.bs.modal', function(e) {
        $('.modal-content').html('');
        $(this).removeData('bs.modal');
    });

    $('#presave').on('click', function(e){
        e.preventDefault();
        $('#confirm').removeClass('hidden');
        $('#body-cache').addClass('cache');
        $(this).hide();
    });


    $('#unconfirm').on('click', function(e){
        e.preventDefault();
        $('#confirm').addClass('hidden');
        $('#body-cache').removeClass('cache');
        $('#presave').show();
    });
    
    $('.carousel').carousel({
      interval: false
    });
    
	$('#dataTable').dataTable({
		'aoColumnDefs': [
    	    {'bSortable': false, 'aTargets': ['nosort']},
    	    {'bSearchable': false, "aTargets": ['nosort']}
		]
	});
		
	$('#posTable').dataTable({
	    "paging": true,
	    "bFilter": false,
		'aoColumnDefs': [
    	    {'bSortable': false, 'aTargets': ['nosort']},
    	    {'bSearchable': false, "aTargets": ['nosort']}
		]
		});
		

});
