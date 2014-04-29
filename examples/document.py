from treepace import Tree, XmlText

XML = '''\
<article>
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

doc = Tree.load(XML, XmlText)
doc.transform('''
    article -> html < body
    heading -> h1
    content -> p
    calc < plus < elem<{.}>, elem<{.}> -> [text(num($1) + num($2))]
''')
print(doc.save(XmlText))