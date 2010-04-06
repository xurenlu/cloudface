#coding:utf8
import _scws
print "hello"
_scws.scws_new()
_scws.scws_set_charset("UTF8")
_scws.scws_set_xdb("/etc/scws/dict.utf8.xdb")
_scws.scws_set_rule("/etc/scws/rules.utf8.ini")
d=_scws.get_res("我们是很好很好的好朋友啊,列宁说")
text="陈凯歌并不是《无极》的唯一著作权人，一部电影的整体版权归电影制片厂所有。 一部电影的作者包括导演、摄影、编剧等创作人员，这些创作人员对他们的创作是有版权的。不经过制片人授权，其他人不能对电影做拷贝、发行、反映，不能通过网络来传播，既不能把电影改编成小说、连环画等其他艺术形式发表，也不能把一部几个小时才能放完的电影改编成半个小时就能放完的短片。 著作权和版权在我国是同一个概念，是法律赋予作品创作者的专有权利。所谓专有权利就是没有经过权利人许可又不是法律规定的例外，要使用这个作品，就必须经过作者授权，没有授权就是侵权。"
text=open("./18.txt").read()
for c in d:
    print c[0]
    print c[1]
    print c[2]
print "exit..."
print d

tops=_scws.get_tops(text,10,"~v")
for top  in tops:
    print top[0],top[1],top[2],top[3]
print "\n======================\n"
tops=_scws.get_tops(text,10,"n")
for top  in tops:
    print top[0],top[1],top[2],top[3]
