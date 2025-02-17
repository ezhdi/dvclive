from pathlib import Path

from mmcv.runner.dist_utils import master_only
from mmcv.runner.hooks import HOOKS
from mmcv.runner.hooks.logger.base import LoggerHook

import dvclive


@HOOKS.register_module()
class DVCLiveLoggerHook(LoggerHook):
    """Class to log metrics with dvclive.

    It requires `dvclive`_ to be installed.

    Args:
        model_file (str):
            Default None.
            If not None, after each epoch the model will
            be saved to {model_file}.
        interval (int): Logging interval (every k iterations).
            Default 10.
            If `by_epoch` is True, the value will be set to 0 in
            order to properly work with `dvclive`_.
        ignore_last (bool): Ignore the log of last iterations in each epoch
            if less than `interval`.
            Default: True.
        reset_flag (bool): Whether to clear the output buffer after logging.
            Default: False.
        by_epoch (bool): Whether EpochBasedRunner is used.
            Default: True.

    .. _dvclive:
        https://dvc.org/doc/dvclive
    """

    def __init__(
        self,
        model_file=None,
        interval=1,
        ignore_last=True,
        reset_flag=False,
        by_epoch=True,
    ):
        self.model_file = model_file
        super().__init__(interval, ignore_last, reset_flag, by_epoch)

    @master_only
    def log(self, runner):
        tags = self.get_loggable_tags(runner)
        if tags:
            for k, v in tags.items():
                step = self.get_iter(runner)
                dvclive.log(k, v, step=step)

    @master_only
    def after_train_epoch(self, runner):
        super().after_train_epoch(runner)
        if self.model_file is not None:
            runner.save_checkpoint(
                Path(self.model_file).parent,
                filename_tmpl=Path(self.model_file).name,
                create_symlink=False,
            )
