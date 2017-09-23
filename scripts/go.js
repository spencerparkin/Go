/* go.js */

var OnNewGameClicked = function() {
    name = prompt( 'Please enter a name for your new game.', '' );
    if( name != null ) {
        $.getJSON( 'new_game', { 'name' : name }, function( json_data ) {
            if( json_data.error )
                window.location.replace( '/error_page?error=' + json_data.error );
            else
                window.location.reload();
        } );
    }
}

var OnJoinGameClicked = function( name, color ) {
    player_name = prompt( 'Please enter your name.', '' );
    if( player_name != null ) {
        $.getJSON( 'join_game', { 'name' : name, 'color' : color, 'player_name' : player_name }, function( json_data ) {
            if( json_data.error )
                window.location.replace( '/error_page?error=' + json_data.error );
            else
                window.location.replace( '/game?name=' + name + '&color=' + color )
        } );
    }
}

var OnPlaceStoneClicked = function( name, color, row, col ) {
    $.getJSON( 'place_stone', { 'name' : name, 'color' : color, 'row' : row, 'col' : col }, function( json_data ) {
        if( json_data.error )
            window.location.replace( '/error_page?error=' + json_data.error );
        else
            window.location.reload();
    } );
}