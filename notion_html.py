# Translate notion element labels to html tags
html_tags = {
    'header': 'h1',
    'sub_header': 'h2',
    'sub_sub_header': 'h3',
    'text': 'p',
    'divider': 'hr',
    'bulleted_list': 'ul',
    'bookmark': 'a'
}

# Class to generate engineering notebook HTML
class HTMLGenerator:

    def __init__(self, client):
        self.client = client

    # Close <b> tags
    def close_tag(self, str):
        ret = ''
        tag = 0
        for char in str:
            ret += char

            if char == '<':
                if tag % 2 != 0:
                    ret += '/'

                tag += 1

        return ret

    # Format bold text
    def format(self, text):
        new_text = self.close_tag(text.replace('__', '<b>'))

        if new_text == text:
            new_text = self.close_tag(text.replace('_', '<i>'))

        return new_text

    # Convert notion block to HTML
    def convert_to_html(self, block):
        tag = html_tags.get(block.type)

        if tag is not None:
            o = '<' + tag + '>'
            c = '</' + tag + '>'

            if tag == 'a':
                return o + c
            elif tag == 'hr':
                return o
            else:
                try:
                    return o + self.format(block.title) + c
                except Exception as e:
                    return ''
        else:
            return ''

    # Get notebook entries as HTML
    def get_sprint_html(self):
        html = ''
        SPRINT_URL = 'https://www.notion.so/dc442ead4ce24653b3fbbec56c9da987?v=7ee74fbb66e64423becf2885396e6987'
        cv = self.client.get_collection_view(SPRINT_URL)

        for card in cv.collection.get_rows():
            id_formatted = ''.join(card.id.split('-'))
            card_page = self.client.get_block('https://www.notion.so/' + card.title + '-' + id_formatted)

            card_html = '<div class="card"><h1>' + card.title + '</h1>'
            additional_html = ''

            i = 0
            for block in card_page.children:
                i += 1
                additional_html += self.convert_to_html(block)

            if additional_html != '':
                card_html += additional_html + '</div>'
                html += card_html

        return html
