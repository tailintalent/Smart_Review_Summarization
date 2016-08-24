function renderResult(d,tStatus, jqxhr){
    product_id = d;
    var resultUrl = "/srs_result_box_bokeh/" + product_id;
    window.location = resultUrl;

    // $("#progress")[0].innerHTML = "Done! Please check your results below.";
    // $("#resultLink")[0].href = resultUrl;
    // $("#resultLink")[0].innerHTML = product_id+" srs result";
    // document.getElementById("loader").style.display = "block";
}

function linspace(a,b,n) {
    if(typeof n === "undefined") n = Math.max(Math.round(b-a)+1,1);
    if(n<2) { return n===1?[a]:[]; }
    var i,ret = Array(n);
    n--;
    for(i=n;i>=0;i--) { ret[i] = (i*b+(n-i)*a)/n; }
    return ret;
}

function fillHistData(cb_data, histPlot_data, features, hist_data) {

    var current_index = cb_data.index['1d'].indices[0];

    if (typeof current_index != 'undefined'){

        histTop = hist_data['tops'][current_index];
        histLeft = hist_data['lefts'][current_index];
        histRight = hist_data['rights'][current_index];
        feature = features[current_index];

        bin_num = histTop.length;
        //Defining the drawing parameters for Fig2
        histPlot_data['bottom'] = new Array(bin_num).fill(0);
        histPlot_data['top'] = histTop;
        histPlot_data['left']= histLeft;
        histPlot_data['right']= histRight;
        histPlot_data['feature'] = feature;

        // console.log(histPlot_data['feature']);
        $("#histPlotTitle p").text(histPlot_data['feature']);           
        }
    
}

function fillHistData_compare(cb_data, histPlot_data1, hist_data1, histPlot_data2, hist_data2, features) {
    var current_index = cb_data.index['1d'].indices[0];


    if (typeof current_index != 'undefined'){
        // console.log(current_index);

        feature = features[current_index];

        histTop1 = hist_data1['tops'][current_index];
        histLeft1 = hist_data1['lefts'][current_index];
        histRight1 = hist_data1['rights'][current_index];

        bin_num1 = histTop1.length;
        //Defining the drawing parameters for Fig2
        histPlot_data1['bottom'] = new Array(bin_num1).fill(0);
        histPlot_data1['top'] = histTop1;
        histPlot_data1['left']= histLeft1;
        histPlot_data1['right']= histRight1;
        histPlot_data1['feature'] = feature;

        histTop2 = hist_data2['tops'][current_index];
        histLeft2 = hist_data2['lefts'][current_index];
        histRight2 = hist_data2['rights'][current_index];

        bin_num2 = histTop2.length;
        //Defining the drawing parameters for Fig2
        histPlot_data2['bottom'] = new Array(bin_num2).fill(0);
        histPlot_data2['top'] = histTop2;
        histPlot_data2['left']= histLeft2;
        histPlot_data2['right']= histRight2;
        histPlot_data2['feature'] = feature;

        // console.log(feature);
        $("#histPlotTitle p").text(feature); 
    }
}
function fillSampleReviews(cb_data, sampleSentences_dict, feature) {
    var barIdx = cb_data.index['1d'].indices[0];

    if (typeof barIdx != 'undefined'){
        var example_sen = sampleSentences_dict[feature][barIdx];
        // console.log(example_sen[0]);
        $("#sample_sen1").text(example_sen[0]);
    }
}

$("#input_form").submit(function(e){    
    var user_input1 = document.forms['input_form'].elements['product_id'].value;
    var user_input2 = document.forms['input_form'].elements['product_id2'].value;
    if (user_input1 == "" && user_input2 == ""){
        $.ajax({
            type: "POST",
            url: "/",
            complete: function(){
                $("#input1_alert").text("Cannot leave empty");
            }
        })
        e.preventDefault();

    }else{
        if (user_input1 == "" && user_input2 != ""){
            document.forms['input_form'].elements['product_id'].value = user_input2;
            document.forms['input_form'].elements['product_id2'].value = "";
        }
        var formData = new FormData($(this)[0]);
        $("#input1_alert").text("");
        // create job
        $.ajax({
            type: "POST",
            url: "/scrape_reviews",
            data: formData,
            async: true,
            success: function(data){
                // alert("Your summarization for " + data + " is ready!");
                // run job (see srs_web.py scrape_reviews for code name)
                id = data;
                if(id=="0"){
                    $("#input1_alert").text("Product category currently not supported"); 
                    $("#input2_alert").text("");
                }
                else if (id=="00"){
                    $("#input1_alert").text("Product category currently not supported"); 
                    $("#input2_alert").text("Product category currently not supported");
                }
                else if (id=="1"){
                    $("#input1_alert").text("Unable to retrieve review from Amazon"); 
                    $("#input2_alert").text("");
                }else if (id=="2") {
                    $("#input1_alert").text("");
                    $("#input2_alert").text("Unable to retrieve review from Amazon"); 
                }else if (id=="12"){
                    $("#input1_alert").text("Unable to retrieve review from Amazon"); 
                    $("#input2_alert").text("Unable to retrieve review from Amazon"); 
                }else if (id=="10"){
                    $("#input1_alert").text("Unable to retrieve review from Amazon");
                    $("#input2_alert").text("Product category currently not supported");

                }else if(id=="02"){
                    $("#input1_alert").text("Product category currently not supported");
                    $("#input2_alert").text("Unable to retrieve review from Amazon");
                }
                else{
                    renderResult(id);
                    $("#input1_alert").text("");
                    $("#input2_alert").text("");
                }
                // $("#loader-wrapper").hide();
                animEl = document.querySelector('.la-anim-5');
                classie.remove( animEl, 'la-animate' );

            },
            beforeSend: function() {
                // $("#loader-wrapper").show();
                animEl = document.querySelector('.la-anim-5');
                classie.add( animEl, 'la-animate' );

            },
            cache: false,
            contentType: false,
            processData: false
        })
        e.preventDefault();
    }
})

$(document).ready(function(){
    $("#addInput2").click(function(e){
        $("#input2").show();
        var Summarize_Button = document.getElementById('Summarize');
        Summarize_Button.value= 'Compare';      
        $("main_section").css({"padding-bottom": "10px"});
        e.preventDefault();
    });
    $("#hideInput2").click(function(e){
        $("#input2").hide();
        var Summarize_Button = document.getElementById('Summarize');
        Summarize_Button.value= 'Summarize';
        e.preventDefault();
    }); 

    // when hit the enter key, form is submitted. 
    $('form').bind('keypress', function(e){
        if ( e.keyCode == 13 ) {
            $(this).find( 'input[type=submit]:first').click();

            if (document.forms['input_form'].elements['product_id2'].value == ""){
                // hide input 2 because by default, it opens inputs 2
                $("#input2").hide();
                var Summarize_Button = document.getElementById('Summarize');
                Summarize_Button.value= 'Summarize';
                e.preventDefault();
            }
        }
    });

});
