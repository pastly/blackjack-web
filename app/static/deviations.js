class Deviation {
    constructor(player, dealer, is_pair, index, action_above) {
        this.player = player;
        this.dealer = dealer;
        this.is_pair = is_pair;
        this.index = index;
        this.action_above = action_above;
        this.action_below = convert_action_above_to_below(action_above);
    }
}

DEVIATIONS = [
    new Deviation( 9,  2, false,  1,     "double"),
    new Deviation( 9,  7, false,  3,     "double"),
    new Deviation(10, 10, false,  4,     "double"),
    new Deviation(10, 11, false,  4,     "double"),
    new Deviation(11, 11, false,  1,     "double"),
    new Deviation(12,  2, false,  3,      "stand"),
    new Deviation(12,  3, false,  2,      "stand"),
    new Deviation(12,  4, false,  0,      "stand"),
    new Deviation(12,  5, false, -2,      "stand"),
    new Deviation(12,  6, false, -1,      "stand"),
    new Deviation(13,  2, false, -1,      "stand"),
    new Deviation(13,  3, false, -2,      "stand"),
    new Deviation(15, 10, false,  4,      "stand"),
    new Deviation(16,  9, false,  5,      "stand"),
    new Deviation(16, 10, false,  0,      "stand"),
    new Deviation(10,  5,  true,  5,      "split"),
    new Deviation(10,  6,  true,  4,      "split"),
    //new Deviation(14, 10, false,  3,  "surrender"),
    //new Deviation(15,  9, false,  2,  "surrender"),
    //new Deviation(15, 10, false,  0,  "surrender"),
    //new Deviation(15, 11, false,  1,  "surrender"),
]

let correct_play = "none";
let current_deviation = null;
let current_true_count = null;

function convert_action_above_to_below(action_above) {
    if (action_above == "double") {
        return "hit";
    } else if (action_above == "stand") {
        return "hit";
    } else if (action_above == "split") {
        return "stand";
    } else if (action_above == "surrender") {
        return "hit";
    } else {
        return "unknown";
    }
}

// Get a random int in [min, max)
function rand_int(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min) + min);
}

function rand_item(list) {
    return list[rand_int(0, list.length)];
}

function on_button(button_name) {
    switch (button_name) {
        case "next":
            return next();
        case "hit":
        case "stand":
        case "double":
        case "split":
        case "surrender":
            return on_button_action(button_name);
        default:
            console.log(button_name + " button pressed, but don't know how to handle it");
    }
}

function get_form_int(input_id) {
    return parseInt(document.getElementById(input_id).value);
}

// Get a string for a card matching the given value
//
// 11 is Ace. 2 - 9 are obvious. 10 will pick uniformally at random from 10,
// J, Q, and K.
//
// A suit is picked at random.
//
// https://stackoverflow.com/a/19557830
// http://www.russellcottrell.com/greek/utilities/SurrogatePairCalculator.htm
function card_char(card_val) {
    let CARDS = "🂡🂱🃁🃑🂢🂲🃂🃒🂣🂳🃃🃓🂤🂴🃄🃔🂥🂵🃅🃕🂦🂶🃆🃖🂧🂷🃇🃗🂨🂸🃈🃘🂩🂹🃉🃙🂪🂺🃊🃚🂫🂻🃋🃛🂭🂽🃍🃝🂮🂾🃎🃞 ";
    // Convert 11 (Ace) to 1 and pick a random version of 10
    if (card_val == 11) {
        card_val = 1;
    } else if (card_val == 10) {
        card_val = rand_int(10, 13+1);
    }
    // Convert card value to first-level index into CARDS string:
    //     *4 for 4 suits, so each "index" is 4 items long
    //     -1 because first item, ace, is 1, so make it 0
    let index = (card_val - 1) * 4;
    // Pick a random suit and increment index to it
    index += rand_int(0, 4);
    // Each card "char" in the CARDS string is actually a pair unicode
    // surrogate things. So the index must be x2, and return the other item in
    // pair too.
    return CARDS.slice(index * 2, index * 2 + 2);
}

// Generate 2 random cards that add up to the given hard hand value and return them as a string
function hard_hand(total_val) {
    // min card val is 2 (no aces)
    // max card val is 2 less than the total (to leave room for second card
    // being a 2). rand_int returns something less than (but not equal) to
    // second argument, so only subtract 1
    let first = rand_int(2, total_val - 1);
    while (first >= 11 || total_val - first >= 11) {
        first = rand_int(2, total_val - 1);
    }
    let second = total_val - first;
    return card_char(first) + card_char(second);
}

// Generate 2 random cards that each have the given value and return them as a string
function pair_hand(card_val) {
    return card_char(card_val) + card_char(card_val);
}

function update_display(deviation, true_count) {
    let player_cards = deviation.is_pair ? pair_hand(deviation.player) : hard_hand(deviation.player);
    let dealer_cards = card_char(deviation.dealer);
    document.getElementById("player_cards").innerText = player_cards;
    document.getElementById("dealer_cards").innerText = dealer_cards;
    document.getElementById("true_count").innerText = true_count;
    //console.log(deviation.player, deviation.is_pair, player_cards);
    //console.log(deviation.dealer, dealer_cards);
}

function show_if_correct(chosen, correct, deviation, true_count) {
    let elm = document.getElementById("hint");
    if (chosen == correct) {
        elm.classList.remove("error");
    } else {
        elm.classList.add("error");
    }
    elm.classList.remove("hide");
    let player_s = deviation.is_pair ?
        deviation.player + "," + deviation.player :
        deviation.player;
    let s = "Correct action with " + player_s + " v " + deviation.dealer +
        " (TC " + true_count + ") is " + deviation.action_above + " >="
        + deviation.index + ", else " + deviation.action_below + ".";
    elm.innerText = s;
}

function next() {
    let min_tc = get_form_int("min_tc");
    let max_tc = get_form_int("max_tc");
    current_true_count = rand_int(min_tc, max_tc + 1);
    current_deviation = rand_item(DEVIATIONS);
    update_display(current_deviation, current_true_count);
    correct_play = current_true_count >= current_deviation.index ?
        current_deviation.action_above : current_deviation.action_below;
}

function on_button_action(action) {
    show_if_correct(action, correct_play, current_deviation, current_true_count);
    next();
}

window.onload = next;
