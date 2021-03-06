
$(document).ready(function () 
{

    //////////////////////////////////
    /// Gene Selection
    //////////////////////////////////
    var $gene_select = $('#gene-select').selectize({
        preload: true,
        valueField: 'gene_symbol',
        labelField: 'gene_symbol',
        searchField: 'gene_symbol',
        render: {
            option: function (item, escape) {
                return '<div class="pt-2 light">'+item.gene_symbol+'</div>';
            }
        },
        load: function (query, callback) {
            // if (!query.length) return callback();
            $.ajax({
                url: "api/genes",//"{{ url_for('genes_api') }}",
                dataType: 'json',
                error: function () {
                    callback();
                },
                success: function (res) {
                    callback(res);
                }
            });
        }
    });

    //////////////////////////////////
    /// Boxplot
    //////////////////////////////////
    // 1. Plotting function
    function boxplot() {

        // Change Status
        $('#boxplot').addClass('loading');

        // Gene
        var gene_symbol = $('#gene-select').val();
        if (!gene_symbol.length) {
            gene_symbol = 'A1BG';
        }

        // Conditions
        var conditions = [];
        $('.condition-btn.plotted').each(function() { conditions.push($(this).attr('data-group_string')) }); conditions

        // AJAX Query
        $.ajax({
            url: "api/plot", //"{{ url_for('plot_api') }}",
            method: 'post',
            data: JSON.stringify({'gene_symbol': gene_symbol, 'conditions': conditions}),
            contentType: 'application/json',
            dataType: 'json',
            error: function () {
                alert('Sorry, there has been an error generating the plot. Please try again.')
            },
            success: function (res) {
                $('#boxplot').removeClass('loading');
                Plotly.newPlot('boxplot', res['data'], res['layout'], config={responsive: true});
            }
        });

    }

    // 2. Listeners
    // Gene
    var boxplot_selectize = $gene_select[0].selectize;
    boxplot_selectize.on('change', function(value) {
        boxplot();
    })

    // Conditions
    $('.condition-btn').on('click', function(evt) {
        $(this).toggleClass('plotted');
        boxplot();
    })

    // 3. Plot
    boxplot();

})
