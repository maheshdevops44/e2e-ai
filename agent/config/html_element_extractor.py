from bs4 import BeautifulSoup
import re

def extract_elements_from_html(html_content):
    """
    Extract various elements from HTML content using BeautifulSoup
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    extracted_data = {
        'buttons': [],
        'spans': [],
        'data_attributes': [],
        'classes': [],
        'test_ids': []
    }
    
    # Extract all buttons
    buttons = soup.find_all('button')
    for button in buttons:
        button_info = {
            'text': button.get_text(strip=True),
            'class': button.get('class', []),
            'data_test_id': button.get('data-test-id'),
            'name': button.get('name'),
            'type': button.get('type'),
            'role': button.get('role'),
            'aria_haspopup': button.get('aria-haspopup')
        }
        extracted_data['buttons'].append(button_info)
    
    # Extract all spans with data attributes
    spans = soup.find_all('span')
    for span in spans:
        span_info = {
            'class': span.get('class', []),
            'data_template': span.get('data-template'),
            'data_ui_meta': span.get('data-ui-meta'),
            'style': span.get('style'),
            'text': span.get_text(strip=True)
        }
        extracted_data['spans'].append(span_info)
    
    # Extract all elements with data attributes
    data_elements = soup.find_all(attrs={'data-test-id': True})
    for element in data_elements:
        data_info = {
            'tag': element.name,
            'data_test_id': element.get('data-test-id'),
            'class': element.get('class', []),
            'text': element.get_text(strip=True)
        }
        extracted_data['data_attributes'].append(data_info)
    
    # Extract all classes
    all_elements = soup.find_all()
    for element in all_elements:
        classes = element.get('class', [])
        if classes:
            extracted_data['classes'].extend(classes)
    
    # Remove duplicates from classes
    extracted_data['classes'] = list(set(extracted_data['classes']))
    
    # Extract test IDs
    test_id_elements = soup.find_all(attrs={'data-test-id': True})
    for element in test_id_elements:
        extracted_data['test_ids'].append(element.get('data-test-id'))
    
    return extracted_data

def print_extracted_data(data):
    """
    Print the extracted data in a formatted way
    """
    print("=== EXTRACTED ELEMENTS ===\n")
    
    print("🔘 BUTTONS:")
    for i, button in enumerate(data['buttons'], 1):
        print(f"  {i}. Test ID: {button['data_test_id']}")
        print(f"     Name: {button['name']}")
        print(f"     Type: {button['type']}")
        print(f"     Classes: {button['class']}")
        print(f"     Role: {button['role']}")
        print(f"     Text: {button['text']}")
        print()
    
    print("📋 SPANS WITH DATA ATTRIBUTES:")
    for i, span in enumerate(data['spans'], 1):
        if span['data_template'] or span['data_ui_meta']:
            print(f"  {i}. Data Template: {span['data_template']}")
            print(f"     Data UI Meta: {span['data_ui_meta']}")
            print(f"     Classes: {span['class']}")
            print(f"     Style: {span['style']}")
            print()
    
    print("🏷️  TEST IDs:")
    for test_id in data['test_ids']:
        print(f"  - {test_id}")
    print()
    
    print("🎨 UNIQUE CLASSES:")
    for class_name in data['classes']:
        print(f"  - {class_name}")
    print()
    
    print("📊 DATA ATTRIBUTES:")
    for i, attr in enumerate(data['data_attributes'], 1):
        print(f"  {i}. Tag: {attr['tag']}")
        print(f"     Test ID: {attr['data_test_id']}")
        print(f"     Classes: {attr['class']}")
        print(f"     Text: {attr['text']}")
        print()

# Example usage with your HTML
if __name__ == "__main__":
    html_content = '''<span data-template="" class="header-element header-title-table  " style="height:30px;width:40px; " data-ui-meta="{'type':'Cell','subType':'pxButton','className':'Data-Portal-DesignerStudio','pgRef':'.pySections(1).pyHeaderTable.pyRows(1).pyCells(1)'}">
        <nobr>
        <span data-template="">
 <button data-test-id="2014091903171702718563" data-ctl="" data-click="[[&quot;showMenu&quot;,[{&quot;dataSource&quot;:&quot;pzManageRecents&quot;, &quot;isNavNLDeferLoaded&quot;:&quot;false&quot;, &quot;isNavTypeCustom&quot;:&quot;false&quot;, &quot;className&quot;:&quot;Data-Portal-DesignerStudio&quot;,&quot;UITemplatingStatus&quot;:&quot;Y&quot;,&quot;menuAlign&quot;:&quot;left&quot;,&quot;format&quot;:&quot;menu-format-standard&quot; , &quot;loadBehavior&quot;:&quot;&quot;, &quot;ellipsisAfter&quot;:&quot;999&quot;,&quot;usingPage&quot;:&quot;pyDisplayHarness&quot;, &quot;useNewMenu&quot;:&quot;true&quot;, &quot;isMobile&quot;:&quot;false&quot;, &quot;navPageName&quot;:&quot;pyNavigation1701725467728&quot;},&quot;:event&quot;]]]" name="pzRecentExplorer_pyDisplayHarness_11" class="Icon_light pzhc pzbutton" type="button" role="button" aria-haspopup="true"><i aria-hidden="true" class="pi pi-caret-down" data-click="."></i></button>
</span>
        </nobr>
    </span>'''
    
    extracted_data = extract_elements_from_html(html_content)
    print_extracted_data(extracted_data)
