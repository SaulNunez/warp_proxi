import sys
from warp.representation.html.table import ColumnAlignment, TableElement
from warp.representation.html.text import AHtmlElement, BigTextHtmlElement, BoldTextHtmlElement, \
    ItalicTextElement, ParagraphHtmlElement, PreformattedText, SmallTextHtmlElement, \
    StrongTextHtmlElement, UnderlineTextElement
from warp.representation.markup import Card
import xml.etree.ElementTree as ET
from html_render.link_creator import ProxiLinkCreator


class RenderToHtml():
    def __init__(self, card: Card, link_creator: ProxiLinkCreator):
        self.card = card
        self.link_creator = link_creator

    def generate(self) -> str:
        root = ET.Element("div")
        for element in self.card.children:
            self._render_paragraph(root, element)
        tree = ET.ElementTree(root)
        return ET.tostring(tree, encoding='unicode')

    def _render_paragraph(self, root, paragraph: ParagraphHtmlElement):
        paragraph = ET.SubElement(root, "p")
        for child in paragraph.children:
            match child:
                case StrongTextHtmlElement():
                    self._render_strong(paragraph, child)
                case ItalicTextElement():
                    self._render_italic(paragraph, child)
                case BoldTextHtmlElement():
                    self._render_bold(paragraph, child)
                case SmallTextHtmlElement():
                    self._render_small(paragraph, child)
                case BigTextHtmlElement():
                    self._render_big(paragraph, child)
                case UnderlineTextElement():
                    self._render_underline(paragraph, child)
                case PreformattedText():
                    self._render_pre(paragraph, child)
                case TableElement():
                    self._render_table(paragraph, child)
                case AHtmlElement():
                    self._render_a(paragraph, child, self.link_creator)
                case _:
                    print(f"Unsupported tag! {child}", file=sys.stderr)
                
        return paragraph

    @staticmethod
    def _align_style_for_column(alignment: ColumnAlignment):
        match alignment:
            case ColumnAlignment.right:
                return "text-align: right;"
            case ColumnAlignment.center:
                return "text-align: center;"
            case _:
                return ""

    @staticmethod
    def _render_table(parent, table: TableElement) -> ET.Element:
        table = ET.SubElement(parent, "table")
        align_colgroup = ET.SubElement(table, "colgroup")
        for i in range(table.columns):
            ET.SubElement(align_colgroup, "col", 
                attrib={'styles': RenderToHtml._align_style_for_column(table.column_alignment(i))})
        for row in table.rows:
            row_elem = ET.SubElement(table, "tr")
            for column in row.columns:
                td = ET.SubElement(row_elem, "td")
                td.text = column.content
        return table
    
    @staticmethod
    def _render_a(parent, strong_text: AHtmlElement, link_creator: ProxiLinkCreator) -> ET.Element:
        strong = ET.SubElement(parent, "a", 
            attrib={"href", link_creator.create_for_url(strong_text.href)})
        strong.text = strong_text.content
        return strong

    @staticmethod
    def _render_anchor() -> ET.Element:
        pass

    @staticmethod
    def _render_strong(parent, strong_text: StrongTextHtmlElement) -> ET.Element:
        strong = ET.SubElement(parent, "strong")
        strong.text = strong_text.content
        return strong

    @staticmethod
    def _render_italic(parent, strong_text: ItalicTextElement) -> ET.Element:
        italic = ET.SubElement(parent, "i")
        italic.text = strong_text.content
        return italic

    @staticmethod
    def _render_bold(parent, bold_text: BoldTextHtmlElement) -> ET.Element:
        bold = ET.SubElement(parent, "b")
        bold.text = bold_text.content
        return bold
    
    @staticmethod
    def _render_small(parent, small_text: SmallTextHtmlElement) -> ET.Element:
        small = ET.SubElement(parent, "small")
        small.text = small_text.content
        return small

    @staticmethod
    def _render_big(parent, big_text: BigTextHtmlElement) -> ET.Element:
        big = ET.SubElement(parent, "big")
        big.text = big_text.content
        return big
    
    @staticmethod
    def _render_underline(parent, big_text: UnderlineTextElement) -> ET.Element:
        underline = ET.SubElement(parent, "u")
        underline.text = big_text.content
        return underline
    
    @staticmethod
    def _render_pre(parent, pre_text: PreformattedText) -> ET.Element:
        pre = ET.SubElement(parent, "pre")
        pre.text = pre_text.content
        return pre