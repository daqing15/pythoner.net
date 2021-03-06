#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User
import datetime

class Tag(models.Model):
    name = models.CharField('tagname',max_length=10,unique=True)
    remark = models.CharField('remark',max_length=300,blank=True,null=True)

    def __unicode__(self):
        if self.remark:
            return u'%s （%s）' %(self.name,self.remark[:100])
        else:
            return self.name

    def get_absolute_url(self):
        return '/topic/%s/' %self.name

    def save(self):
        self.name = self.name.strip()
        super(Tag,self).save()

class Topic(models.Model):
    title = models.CharField('标题',max_length=50)
    author = models.ForeignKey(User,verbose_name='作者',related_name='author')
    deleted = models.BooleanField('删除',default=False)
    top = models.BooleanField('置顶',default=False)
    ip = models.IPAddressField('IP',default='127.0.0.1')
    sub_time = models.DateTimeField('时间',auto_now_add=True)
    latest_response = models.DateTimeField('最后回复',null=True,blank=True)
    click_times = models.PositiveIntegerField('点击次数',max_length=10,default=0,editable=False)
    content = models.TextField('内容',blank=False,null=False)
    tag = models.ManyToManyField(Tag,verbose_name='标签',blank=True,null=True,editable=True)
    notice = models.BooleanField('是否通知作者',default=True)

    class Meta:
        ordering = ['deleted','-top','-latest_response','-sub_time','author','-click_times']

    def __unicode__(self):
        if self.deleted:
            return u'[已删除]%s' %self.title
        else:
            return self.title

    def get_absolute_url(self):
        return '/topic/%d/' %self.id

    def all(self):
        return Topic.objects.filter(deleted=False)

    def view(self):
        """
        Auto increase click times
        """
        self.click_times += 1
        super(Topic,self).save()
    
    def save(self,*args, **kwargs):

        # new topic
        if self.id is None:
            super(Topic,self).save(*args, **kwargs)
        else:

            # edit topic
            self.tag.clear()

        # get system tags
        tag_list = Tag.objects.all()

        # Auto creat tag when topic is be saved
        for tag in tag_list:
            content = self.title+self.content
            if content.lower().count(tag.name.lower()) > 0:
                self.tag.add(tag)
                del tag
                continue

        super(Topic,self).save(*args, **kwargs)

class Favorite(models.Model):
    user = models.ForeignKey(User)
    topic = models.ForeignKey(Topic)
