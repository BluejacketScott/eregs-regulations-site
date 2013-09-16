define("sidebar-view",["jquery","underscore","backbone","dispatch","sidebar-head-view","sxs-list-view"],function(e,t,n,r,i,s){var o=n.View.extend({el:"#sidebar-content",events:{"click .expandable":"toggleExpandable"},initialize:function(){r.on("sidebarModule:render",function(e){this.insertChild(e)},this),r.on("sidebarModule:close",function(e){this.removeChild(e)},this),r.on("definition:open",this.closeExpandables,this),r.on("definition:render",this.insertDefinition,this),r.on("search:submitted",this.closeAllChildren,this),r.on("regSection:open",this.openRegFolders,this),this.childViews={},this.openRegFolders()},openRegFolders:function(){this.childViews.sxs=new s},insertChild:function(e){this.$el.append(e)},removeChild:function(t){e(t).remove()},insertDefinition:function(e){this.$el.prepend(e)},closeExpandables:function(){this.$el.find(".expandable").each(function(t,n){var r=e(n);r.hasClass("open")&&this.toggleExpandable(r)}.bind(this))},toggleExpandable:function(t){var n;typeof t.stopPropagation!="undefined"?(t.stopPropagation(),n=e(t.currentTarget)):n=t,n.toggleClass("open").next(".chunk").slideToggle()},closeAllChildren:function(){var e;for(e in this.childViews)this.childViews.hasOwnProperty(e)&&this.childViews[e].remove()}});return o});