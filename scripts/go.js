/* go.js */

var OnNewGameClicked = function() {
    name = prompt( 'Please enter a name for your new game.', '' );
    if( name != null ) {
        size = prompt( 'What size board?  (e.g. enter "5" for a 5x5 board.)' );
        $.getJSON( 'new_game', { 'name' : name, 'size' : size }, function( json_data ) {
            if( json_data.error )
                window.location.replace( '/error_page?error=' + json_data.error );
            else
                window.location.reload();
        } );
    }
}

var OnDeleteGameClicked = function( name ) {
    $.getJSON( 'del_game', { 'name' : name }, function( json_data ) {
        if( json_data.error )
            window.location.replace( '/error_page?error=' + json_data.error );
        else
            window.location.reload();
    } );
}

var OnPlaceStoneClicked = function( name, color, row, col ) {
    $.getJSON( 'place_stone', { 'name' : name, 'color' : color, 'row' : row, 'col' : col }, function( json_data ) {
        if( json_data.error )
            window.location.replace( '/error_page?error=' + json_data.error );
        else
            window.location.reload();
    } );
}