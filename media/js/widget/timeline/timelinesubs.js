// Amara, universalsubtitles.org
//
// Copyright (C) 2012 Participatory Culture Foundation
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see
// http://www.gnu.org/licenses/agpl-3.0.html.

goog.provide('unisubs.timeline.TimelineSubs');
/**
* @constructor
* @extends goog.ui.Component
*/
unisubs.timeline.TimelineSubs = function(subtitleSet, pixelsPerSecond, readOnly) {
    goog.ui.Component.call(this);
    this.subtitleSet_ = subtitleSet;
    this.pixelsPerSecond_ = pixelsPerSecond;
    this.readOnly_ = readOnly;
    /**
     * Map of caption id to TimelineSub
     */
    this.subs_ = {};
};
goog.inherits(unisubs.timeline.TimelineSubs, goog.ui.Component);
unisubs.timeline.TimelineSubs.prototype.createDom = function() {
    unisubs.timeline.TimelineSubs.superClass_.createDom.call(this);
    this.getElement().className = 'unisubs-timeline-subs';
    var subsToDisplay = this.subtitleSet_.getSubsToDisplay();
    var i;
    for (i = 0; i < subsToDisplay.length; i++)
        this.addSub_(subsToDisplay[i]);
};
unisubs.timeline.TimelineSubs.prototype.enterDocument = function() {
    unisubs.timeline.TimelineSubs.superClass_.enterDocument.call(this);
    var ss = unisubs.timeline.SubtitleSet;
    this.getHandler().
        listen(
            this.subtitleSet_,
            ss.DISPLAY_NEW,
            this.displayNewListener_).
        listen(
            this.subtitleSet_,
            ss.REMOVE,
            this.removeListener_);
    // TODO: listen to CLEAR_ALL also (after you write it and unit test :))
};
unisubs.timeline.TimelineSubs.prototype.displayNewListener_ =
    function(event)
{
    this.addSub_(event.subtitle);
};
unisubs.timeline.TimelineSubs.prototype.removeListener_ = function(event) {
    var captionID = event.subtitle.getEditableCaption().getCaptionID();
    var timelineSub = this.subs_[captionID];
    this.removeChild(timelineSub, true);
    delete this.subs_[captionID];
};
unisubs.timeline.TimelineSubs.prototype.addSub_ = function(sub) {
    var timelineSub = new unisubs.timeline.TimelineSub(
        sub, this.pixelsPerSecond_, 0, this.readOnly_);
    this.addChild(timelineSub, true);
    this.subs_[sub.getEditableCaption().getCaptionID()] = timelineSub;
};
