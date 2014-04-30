from treepace import Tree, XmlText
import sys

def main():
    if len(sys.argv) == 2:
        text = open(sys.argv[1]).read()
    else:
        text = '''<article>
                      <heading>An example</heading>
                      <content>
                          <calc>
                              <plus>
                                  <elem>3</elem>
                                  <elem>4</elem>
                              </plus>
                          </calc>
                      </content>
                  </article>'''
    
    doc = Tree.load(text, XmlText)
    doc.transform('''
        article -> html < body
        heading -> h1
        content -> p
        calc < plus < elem<{.}>, elem<{.}> -> [text(num($1) + num($2))]
    ''')
    print(doc.save(XmlText))

if __name__ == '__main__':
    main()