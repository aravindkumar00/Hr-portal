function highlight_search_word(text, search_word) {
    var regex = new RegExp('(' + search_word + ')', 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
}