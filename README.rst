Overview
+++++++++++++++++++++

- HSR-Bのgazebo用設定ファイル、起動ファイルを管理する。

管理ファイル
++++++++++++

launch
^^^^^^

シミュレータ起動用ファイルを管理

* コントローラ+センサ+何もない環境の構成でシミュレータを起動

.. code-block:: bash

                $ roslaunch hsrb_gazebo_bringup hsrb_empty_world.launch

* ゲイン調整用コントローラ+センサ+何もない環境の構成でシミュレータを起動

.. code-block:: bash

                $ roslaunch hsrb_gazebo_bringup hsrb_gain_tuning.launch

params
^^^^^^

コントローラ・センサ用設定ファイルやPIDゲイン設定ファイルを管理する。

LICENSE
+++++++++

This software is released under the BSD 3-Clause Clear License, see LICENSE.txt.
