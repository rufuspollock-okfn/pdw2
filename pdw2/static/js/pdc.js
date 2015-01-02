PDC = {};
PDC.server = "http://publicdomainworks.net/api";
PDC.root = "http://publicdomainworks.net";

function decodeHtml(p_string){
if ((typeof p_string === "string") && (new RegExp(/&amp;|&lt;|&gt;|&quot;|&#39;/).test(p_string)))
    {
        return p_string.replace(/&amp;/g, "&").replace(/&lt/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, "\"").replace(/&#39;/g, "'");
    }

    return p_string;
}

$(function(){
	PDC.showresult = function(data) {

	console.log('showing the results: ' + PDC.title);
        $('#results').empty();
        if (data.output == "" && data.error != ""){
		console.log('ERRORORORORRO');
        	$('#results').append(ich.error({msg:data.error}))
        }else{
		console.log('SUCESSSSSS::::' + data);
		step = data.output.pop();
	step.author = PDC.author;
	step.title = PDC.title;
       		$('#results').append(ich[step.type](step));
		for (var s in data.output){
        		step = data.output[s];
			$('#results').append(ich[step.type](step));
		}
        }
    }

	PDC.queryresults = function(data) {
		$('#search-results').empty();


		$('#search-result').css('height','auto');
		$('#search-result').css('min-height','100%');
		$('#search-result').css('padding-bottom','100px');

		if(data.output == "" && data.error != "") {
			console.log(error);
		} else{
     		        console.log(data[2])
			for (var s in data){
				step = data[s];
				var htmldata = decodeHtml (ich.searchresult(step));
				$('#search-results').append(htmldata);
			}
		}

		$('#searchbutton').button('reset');
	}

	$('#submit').on('click', calculate);
	$(document).on('click', '.calc', calculate);


	function calculate() {

		PDC.author = $(this).data('author'); 
		PDC.title = $(this).data('title');
		console.log("calculating..." + PDC.author + "[[[[[[]]]]" + PDC.title);
		$('#results').empty();
		$('#results').append("Calcul en cours ...");	
	
		jurisdiction = $(this).data('jurisdiction') || $('#jurisdiction').val();
		rdf = $(this).data('rdf') || $('#work').val();

		console.log("work = " + rdf);
		console.log("jurisdiction = " + jurisdiction);

		$.ajax({
			"url":PDC.server+'/pd',
			"data":{
				jurisdiction: "france",
				flavour:"bnf",
				work:$(this).data('rdf') || $('#work').val(),
				detail:$(this).data('detail') || $('#detail').val() || "medium",
				lang:"fr"
			},
			"success": PDC.showresult,
			"dataType":"json",
			"timeout":35000,
			"error":PDC.showresult
		});
	};

	$( "#query-author" ).keypress( function(e) {
	if ( e.which == 13 ) {
	search();
	}

	});

	$( "#query-work" ).keypress( function(e) {
	if ( e.which == 13 ) {
	search();
	}

	});

	$('#searchbutton').on('click', search); 


		function search() {
		
		$("#carousel").carousel('pause');
		console.log( $('#query').val());
		$('#searchbutton').button('loading');

		$.ajax({
			"url":PDC.root+'/list',
			"data":{
				"author": $('#query-author').val(),
				"work": $('#query-work').val()
			},
			"success": PDC.queryresults,
			"dataType":"json",
			"timeout":30000,
			"error":PDC.queryresults,
		});

	};		

});
