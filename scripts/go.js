/* go.js */

var OnNewGameClicked = function() {
    name = prompt( 'Please enter a name for your new game.', '' );
    if( name != null ) {
        size = prompt( 'What size board?  (e.g. enter "5" for a 5x5 board.)' );
        $.getJSON( 'new_game', { 'name' : name, 'size' : size }, function( json_data ) {
            if( json_data.error )
                window.location.assign( '/error_page?error=' + json_data.error );
            else
                window.location.reload();
        } );
    }
}

var OnDeleteGameClicked = function( name ) {
    $.getJSON( 'del_game', { 'name' : name }, function( json_data ) {
        if( json_data.error )
            window.location.assign( '/error_page?error=' + json_data.error );
        else
            window.location.reload();
    } );
}

var OnPlaceStoneClicked = function( name, color, row, col ) {
    respond = $( '#respond:checked' ).length > 0 ? true : false;
    $.getJSON( 'place_stone', { 'name' : name, 'color' : color, 'row' : row, 'col' : col, 'respond' : respond }, function( json_data ) {
        if( json_data.error )
            window.location.assign( '/error_page?error=' + json_data.error );
        else
            window.location.reload();
    } );
}

var OnGiveUpStoneClicked = function( name, color, row, col ) {
    answer = confirm( 'Give up stone?' )
    if( answer ) {
        $.getJSON( 'relinquish_stone', { 'name' : name, 'color' : color, 'row' : row, 'col' : col }, function( json_data ) {
            if( json_data.error ) {
                window.location.assign( '/error_page?error=' + json_data.error );
            } else {
                window.location.reload();
            }
        } );
    }
}

var OnMouseOverStone = function( id_list, visible ) {
    length = id_list.length;
    for( var i = 0; i < length; i++ ) {
        id = id_list[i];
        ele = document.getElementById( id );
        if( ele != null ) {
            if( visible ) {
                ele.style.visibility = "visible";
            } else {
                ele.style.visibility = "hidden";
            }
        }
    }
}