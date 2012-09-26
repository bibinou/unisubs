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

goog.provide('unisubs.CaptionManager');

/**
 * @constructor
 *
 * @param {unisubs.player.AbstractVideoPlayer} videoPlayer
 * @param {unisubs.subtitle.EditableCaptionSet} captionSet
 */
unisubs.CaptionManager = function(videoPlayer, captionSet) {
    goog.events.EventTarget.call(this);

    this.captions_ = captionSet.captionsWithTimes();

    this.binaryCompare_ = function(time, caption) {
	return time - caption.getStartTime();
    };
    this.binaryCaptionCompare_ = function(c0, c1) {
        return c0.getStartTime() - c1.getStartTime();
    };
    this.videoPlayer_ = videoPlayer;
    this.eventHandler_ = new goog.events.EventHandler(this);

    this.eventHandler_.listen(
	videoPlayer,
	unisubs.player.AbstractVideoPlayer.EventType.TIMEUPDATE,
	this.timeUpdate_);
    this.eventHandler_.listen(
	captionSet,
        goog.array.concat(
            goog.object.getValues(
                unisubs.subtitle.EditableCaptionSet.EventType),
            unisubs.subtitle.EditableCaption.CHANGE),
	this.captionSetUpdate_);

    this.currentCaptionIndex_ = -1;
    this.lastCaptionDispatched_ = null;
    this.eventsDisabled_ = false;
};
goog.inherits(unisubs.CaptionManager, goog.events.EventTarget);

unisubs.CaptionManager.CAPTION = 'caption';
unisubs.CaptionManager.CAPTIONS_FINISHED = 'captionsfinished';

unisubs.CaptionManager.prototype.captionSetUpdate_ = function(event) {
    var et = unisubs.subtitle.EditableCaptionSet.EventType;
    if (event.type == et.CLEAR_ALL ||
        event.type == et.CLEAR_TIMES ||
        event.type == et.RESET_SUBS) {
	this.captions_ = [];
        this.currentCaptionIndex_ = -1;
	this.dispatchCaptionEvent_(null);
    }
    else if (event.type == et.ADD) {
        var caption = event.caption;
        if (caption.getStartTime() != -1) {
            goog.array.binaryInsert(
                this.captions_, caption, this.binaryCaptionCompare_);
            this.sendEventForRandomPlayheadTime_(
                this.videoPlayer_.getPlayheadTime());
        }
    }
    else if (event.type == et.DELETE) {
        var caption = event.caption;
        if (caption.getStartTime() != -1) {
            goog.array.binaryRemove(
                this.captions_, caption, this.binaryCaptionCompare_);
            this.sendEventForRandomPlayheadTime_(
                this.videoPlayer_.getPlayheadTime());
        }
    }
    else if (event.type == unisubs.subtitle.EditableCaption.CHANGE) {
	if (event.timesFirstAssigned) {
	    this.captions_.push(event.target);
	    this.timeUpdate_();
	}
    }
};

unisubs.CaptionManager.prototype.timeUpdate_ = function() {
    this.sendEventsForPlayheadTime_(
	this.videoPlayer_.getPlayheadTime());
};

unisubs.CaptionManager.prototype.sendEventsForPlayheadTime_ =
    function(playheadTime)
{
    if (this.captions_.length == 0)
        return;
    if (this.currentCaptionIndex_ == -1 &&
        playheadTime < this.captions_[0].getStartTime())
        return;

    var curCaption = this.currentCaptionIndex_ > -1 ?
        this.captions_[this.currentCaptionIndex_] : null;
    if (this.currentCaptionIndex_ > -1 &&
        curCaption != null &&
	curCaption.isShownAt(playheadTime))
        return;

    var nextCaption = this.currentCaptionIndex_ < this.captions_.length - 1 ?
        this.captions_[this.currentCaptionIndex_ + 1] : null;
    if (nextCaption != null &&
	nextCaption.isShownAt(playheadTime)) {
        this.currentCaptionIndex_++;
        this.dispatchCaptionEvent_(nextCaption);
        return;
    }
    if ((nextCaption == null ||
         playheadTime < nextCaption.getStartTime()) &&
        (curCaption == null ||
         playheadTime >= curCaption.getStartTime())) {
        this.dispatchCaptionEvent_(null);
        if (nextCaption == null && !this.eventsDisabled_)
            this.dispatchEvent(unisubs.CaptionManager.CAPTIONS_FINISHED);
        return;
    }
    this.sendEventForRandomPlayheadTime_(playheadTime);
};

unisubs.CaptionManager.prototype.sendEventForRandomPlayheadTime_ =
    function(playheadTime)
{
    var lastCaptionIndex = goog.array.binarySearch(this.captions_,
        playheadTime, this.binaryCompare_);
    if (lastCaptionIndex < 0)
        lastCaptionIndex = -lastCaptionIndex - 2;
    this.currentCaptionIndex_ = lastCaptionIndex;
    if (lastCaptionIndex >= 0 &&
	this.captions_[lastCaptionIndex].isShownAt(playheadTime)) {
        this.dispatchCaptionEvent_(this.captions_[lastCaptionIndex]);
    }
    else {
        this.dispatchCaptionEvent_(null);
    }
};

unisubs.CaptionManager.prototype.dispatchCaptionEvent_ = function(caption) {
    if (caption == this.lastCaptionDispatched_)
        return;
    if (this.eventsDisabled_)
        return;
    this.lastCaptionDispatched_ = caption;
    this.dispatchEvent(new unisubs.CaptionManager.CaptionEvent(caption));
};

unisubs.CaptionManager.prototype.disposeInternal = function() {
    unisubs.CaptionManager.superClass_.disposeInternal.call(this);
    this.eventHandler_.dispose();
};

unisubs.CaptionManager.prototype.disableCaptionEvents = function(disabled) {
    this.eventsDisabled_ = disabled;
};

/**
* @constructor
*/
unisubs.CaptionManager.CaptionEvent = function(editableCaption) {
    this.type = unisubs.CaptionManager.CAPTION;
    this.caption = editableCaption;
};
