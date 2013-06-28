define("content-view",["jquery","underscore","backbone","jquery-scrollstop","regs-dispatch","definition-view"],function(e,t,n,r,i,s){var o=n.View.extend({openDefinition:{id:"",view:{},link:{}},events:{"click .definition":"definitionLink","click .expand-button":"expandInterp","click .inline-interp-header":"expandInterp","click .inline-interpretation:not(.open)":"expandInterp","mouseenter p":"showPermalink","mouseenter h2.section-number":"showPermalink"},initialize:function(){var n,r;i.on("definition:remove",this.cleanupDefinition,this),i.on("toc:click",this.changeFocus,this),e(window).on("scrollstop",t.bind(this.checkActiveSection,this)),this.$sections={},this.$contentHeader=e("header.reg-header"),this.$contentContainer=this.$el.find(".level-1 li[id], .reg-section, .appendix-section, .supplement-section"),this.activeSection="",this.$activeSection="",this.$window=e(window),n=this.$contentContainer.length;for(r=0;r<n;r++)this.$sections[r]=e(this.$contentContainer[r])},checkActiveSection:function(){var e=this.$contentContainer.length-1;for(var n=0;n<=e;n++)if(this.$sections[n].offset().top+this.$contentHeader.height()>=this.$window.scrollTop())if(t.isEmpty(this.activeSection)||this.activeSection!==this.$sections[n].id){this.activeSection=this.$sections[n][0].id,this.$activeSection=this.$sections[n][0],i.trigger("activeSection:change",this.activeSection);return}return this},cleanupDefinition:function(){return delete this.openDefinition.id,delete this.openDefinition.view,this.openDefinition.link&&this.openDefinition.link.removeClass("active").removeData("active"),delete this.openDefinition.link,delete this.openDefinition.linkText,this},definitionLink:function(n){n.preventDefault();var r=e(n.target),i;return r.data("active")?(this.openDefinition.view.remove(),this):(i=r.attr("data-definition"),r.addClass("active").data("active",1),i===this.openDefinition.id&&r.text().toLowerCase()===this.openDefinition.linkText?(this.openDefinition.link.removeClass("active").removeData("active"),this.openDefinition.link=r,this):(t.isEmpty(this.openDefinition.view)||this.openDefinition.view.remove(),this.storeDefinition(r,i),this))},storeDefinition:function(e,t){this.openDefinition.link=e,this.openDefinition.linkText=e.text().toLowerCase(),this.openDefinition.id=t,this.openDefinition.view=new s({id:t,$anchor:e,linkText:this.openDefinition.linkText})},expandInterp:function(t){t.stopPropagation();var n,r,s;return t.currentTarget.tagName.toUpperCase()==="SECTION"?n=e(t.currentTarget).find(".expand-button"):t.currentTarget.tagName.toUpperCase()==="H4"?n=e(t.currentTarget).siblings(".expand-button"):n=e(t.currentTarget),s=n.parent(),n.toggleClass("open").next(".hidden").slideToggle(),s.toggleClass("open"),r=n.hasClass("open"),n.html(r?"Hide":"Show"),i.trigger("interpretation:toggle",{context:s.data("interpFor"),action:r?"opened":"hid"}),this},showPermalink:function(t){e(".permalink-marker").remove();var n=document.createElement("a"),r=e(t.currentTarget),i,s,o;if(r.parents().hasClass("inline-interpretation"))return;t.currentTarget.tagName.toUpperCase()==="H2"?o=r.parent(".reg-section"):o=r.closest("li"),typeof o[0]!="undefined"&&(i=o[0].id,n.href="#"+i,n.innerHTML="Permalink",s=e(n),e(r).prepend(s),s.addClass("permalink-marker"))},changeFocus:function(t){e(t.context).focus()}});return o});