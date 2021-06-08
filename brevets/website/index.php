<?php

  $webpage = new ACPWebPage();
  $html = $webpage->getHTML();
  echo $html;


class ACPWebPage {
  public function getHTML() {
    $go = '';
    if (array_key_exists('go', $_REQUEST)) {
      $go = $_REQUEST['go'];
    }
    if ($go) {
      $html = $this->getACPTimesResults();
    } else {
      $html = $this->getUserWebHTML();
    }
    return $html;
  }

  protected function getACPTimesData($output_type) {
    $request_file = 'http://'.$_ENV['BACKEND_ADDR'].':'.$_ENV['BACKEND_PORT'].'/';
    $column_type = $_REQUEST['column_type'];
    if (array_key_exists('top', $_REQUEST)) {
      $top = (int) $_REQUEST['top'];
    } else {
      $top = 0;
    }

    // set the column type
    if ($column_type == 'all_columns') {
      $request_file .= 'listAll/';
    } elseif ($column_type == 'open_column') {
      $request_file .= 'listOpenOnly/';
    } elseif ($column_type == 'close_column') {
      $request_file .= 'listCloseOnly/';
    }

    if ($output_type == 'csv') {
      $request_file .= 'csv';
    } else {
      $request_file .= 'json';
    }

    // set the Limit
    $top = $_REQUEST['top'];
    if ($top > 0) {
      $request_file .= '?top='.$top;
    }
    $data = file_get_contents($request_file);
    return $data;

  }

  protected function getACPTimesResults() {
    $html = '';
    $output_type = $_REQUEST['output_type'];
    $data = $this->getACPTimesData($output_type);
    if ($data) {
      if ($output_type == 'table') {
        $json = json_decode($data, true);
        $length = count($json);
        if ($length == 0) {
          $html = '<p>Nothing to display</p>';
        } else {
          $headers = array_keys(current($json));

          $table = '<table border=1>';
          $table .= '<tr>';
          foreach($headers as $header) {
            $table .= '<th>'.$header.'</th>';
          }
          $table .= '</tr>';
          foreach($json as $row) {
            $table .= '<tr>';
            foreach($headers as $header) {
              $table .= '<td>'.$row[$header].'</td>';
            }
            $table .= '</tr>';
          }
          $table .= '</table>';
          $html = $table;
        }
      } else {
        return $data;
      }
    }
    return $html;
  }

  protected function getACPTimesResultsHTML() {
    $header = $this->getHeader('ACP Control Time Results');
    $body = '<body>';
    $body .= $this->getACPTimesResults();
    $body .= '</body>';
    $html = '<html>'.$header.$body.'</html>';
    return $html;
  }

  protected function getUserWebHTML() {
    $header = $this->getHeader('ACP Control Times');

    $body = '<form method="post" action="">';
    $body .= $this->getColumnTypeRadioInput();
    $body .= '<br><br>';
    $body .= $this->getTopTextInput();
    $body .= '<br><br>';
    $body .= $this->getOutputFormatOption();
    $body .= '<br><br>';
    $body .= $this->getGoButton();
    $body .= '</form>';
    $html = '<html>'.$header.$body.'</html>';
    return $html;
  }

  protected function getOutputFormatOption() {
    $radio = '';

    $radio .= '<p>Select the way you would like to see the data.</p>';

    $radio .= '<input type="radio" id="table" name="output_type" value="table" checked>';
    $radio .= '<label for="table">Table</label>';
    $radio .= ' || ';

    $radio .= '<input type="radio" id="csv" name="output_type" value="csv">';
    $radio .= '<label for="csv">CSV</label>';
    $radio .= ' || ';

    $radio .= '<input type="radio" id="json" name="output_type" value="json">';
    $radio .= '<label for="json">JSON</label>';

    return $radio;
  }

  protected function getGoButton() {
    $input = '';
    $input .= '<input type="submit" value="Get Times" name="go">';
    return $input;
  }

  protected function getTopTextInput() {
    $input = '';
    $input .= '<p>If you want to limit how many items come back, please put that number below</p>';
    $input .= '<label for="top">Top limit: </label>';
    $input .= '<input type="text" value="" id="top" name="top">';
    return $input;
  }

  protected function getColumnTypeRadioInput() {
    $radio = '';

    $radio .= '<p>Select the type of columns you would like to retrieve.</p>';

    $radio .= '<input type="radio" id="all_columns" name="column_type" value="all_columns" checked>';
    $radio .= '<label for="all_columns">All</label>';
    $radio .= ' || ';

    $radio .= '<input type="radio" id="open_column" name="column_type" value="open_column">';
    $radio .= '<label for="open_column">Open</label>';
    $radio .= ' || ';

    $radio .= '<input type="radio" id="close_column" name="column_type" value="close_column">';
    $radio .= '<label for="close_column">Close</label>';

    return $radio;
  }
  protected function getHeader($title) {
    $html = '<head>';
    $html .= '<title>'.$title.'</title>';
    $html .= $this->getJavascript();
    $html .= '</head>';
    return $html;
  }

  protected function getJavascript() {
    $javascript = '<script
      src="https://code.jquery.com/jquery-3.6.0.min.js"
      integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4="
      crossorigin="anonymous">
      </script>';
      return $javascript;
  }
}


 ?>
